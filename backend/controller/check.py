''' Check '''
import json
import logging
import os

import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.service import workspace
from backend.util import fileio
from backend.model.attribute import Attribute

class CheckWebSocket(DefaultWSHandler):
    name = "check"

    def open(self):
        logging.info("[ws] Check WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            wid = msg_json.get("wid", None)
            logging.info("[ws] check init: wid=%s", wid)
            if wid is None:
                self.write_json(msg_type="init", err="no_wid")
                return

            self.space = workspace.get_by_id(wid)
            if self.space is None or not self.space.enabled:
                self.write_json(msg_type="init", err="no_workspace")
                return
            self.space.add_ws(self)
            self.write_json(msg_type="init", status="success",
                            data=self.space.serializable())
        elif msg_type == "cancel":
            wid = msg_json.get("wid", None)
            logging.info("[ws] check cancel: wid=%s", wid)
            if wid is None:
                self.write_json(msg_type="cancel", err="no_wid")
                return

            self.space = workspace.get_by_id(wid)
            if self.space is None or not self.space.enabled:
                self.write_json(msg_type="cancel", err="no_workspace")
                return
            self.space.set_cancel("check")
            self.write_json(msg_type="cancel", status="run")

    def on_close(self):
        logging.info("[ws] close")
        if hasattr(self, "space") and self.space is not None:
            self.space.del_ws(self)


class Check(DefaultHandler):
    ''' check '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        check_date = self.get_arg("check_date")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        yield self.check(space, check_date)

    @run_on_executor
    def check(self, space, check_date):
        # get attributes
        attrs = space.driver.get_attrs(check_date=check_date)
        if attrs is None:
            self.write_json(err="db")
            return
        attr_len = len(attrs)
        space.send_ws(name="check", msg_type="check", status="success", data={
            "total": attr_len
        })

        msg_interval = min(1000, max(1, int(attr_len / 1000)))
        if msg_interval <= 0:
            msg_interval = 1
        for i in range(attr_len):
            attr = attrs[i]
            hash_file_name = fileio.format_file_name(
                attr.size, attr.crc32, attr.sha256, None)
            hash_file_path = os.path.abspath(os.path.join(space.data_path, hash_file_name))

            if i % msg_interval == 0:
                space.send_ws(name="check", msg_type="sync", status="run", data={
                    "now": i, "total": attr_len
                })

            # check
            try:
                with open(hash_file_path, 'rb') as f:
                    encrypt_data = f.read()
                encrypt_crc32 = fileio.get_crc_32(encrypt_data)

                # check cancel
                if space.check_cancel("check"):
                    self.write_json(status="cancel", err="cancel", status_code=499)
                    space.send_ws(name="check", msg_type="cancel", status="success")
                    return

                # check `encrypt_crc32` if exist
                if attr.encrypt_crc32 is not None:
                    if encrypt_crc32 != attr.encrypt_crc32:
                        logging.error("[check] check attr %s failed, encrypt_crc32=%s", attr.id, encrypt_crc32)
                        space.send_ws(name="check", msg_type="msg", status="run", data={
                            "msg": f"check attr: {attr.id} failed, encrypt_crc32={encrypt_crc32}"
                        })
                        continue
                else:
                    # check `crc32`
                    if attr.encrypt is not None and attr.key is not None:
                        _, _, crc32 = fileio.decrypt_file_stream(hash_file_path, attr.key, calc_crc_out=True)
                    else:
                        crc32 = encrypt_crc32
                    if crc32 != attr.crc32:
                        logging.error("[check] check attr %s failed, crc32=%s", attr.id, crc32)
                        space.send_ws(name="check", msg_type="msg", status="run", data={
                            "msg": f"check attr: {attr.id} failed, crc32={crc32}"
                        })
                        continue

                # update `encrypt_crc32`
                attr_new = Attribute()
                attr_new.none()
                attr_new.id = attr.id
                attr_new.encrypt_crc32 = encrypt_crc32
                attr_new.check_date = check_date
                update_ok = space.driver.update_attribute(attr_new)
                if not update_ok:
                    space.driver.rollback()
                    logging.error("[check] update attr %s failed, err=%s", attr.id, e)
                    space.send_ws(name="check", msg_type="msg", status="run", data={
                        "msg": f"update attr: {attr.id} failed"
                    })
                    continue
                space.driver.commit()
            except Exception as e:
                logging.error("[check] check attr %s failed, err=%s", attr.id, e)
                space.send_ws(name="check", msg_type="msg", status="run", data={
                    "msg": f"check attr {attr.id} failed"
                })
                continue

        space.send_ws(name="check", msg_type="done", status="success", data={
            "total": attr_len
        })
        self.write_json(status="success", data=attr_len)
        return
