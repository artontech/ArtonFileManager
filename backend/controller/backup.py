''' Backup '''
import json
import logging
import os
import shutil

import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.service import workspace
from backend.util import fileio

class BackupWebSocket(DefaultWSHandler):
    name = "backup"

    def open(self):
        logging.info("[ws] Backup WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            wid = msg_json.get("wid", None)
            logging.info("[ws] backup init: wid=%s", wid)
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

    def on_close(self):
        logging.info("[ws] close")
        if hasattr(self, "space") and self.space is not None:
            self.space.del_ws(self)


class Copy(DefaultHandler):
    ''' copy '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        backup_path = os.path.abspath(self.get_arg("backup_path"))

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        yield self.copy(space, backup_path)

    @run_on_executor
    def copy(self, space, backup_path):
        # get attributes
        attrs = space.driver.get_attrs()
        if attrs is None:
            self.write_json(err="db")
            return
        attr_len = len(attrs)
        space.send_ws(name="backup", msg_type="check", status="success", data={
            "total": attr_len
        })

        msg_interval = min(1000, max(1, int(attr_len / 1000)))
        if msg_interval <= 0:
            msg_interval = 1
        for i in range(attr_len):
            attr = attrs[i]
            hash_file_name = fileio.format_file_name(
                attr.size, attr.crc32, attr.sha256, None)
            src_path = os.path.abspath(os.path.join(space.data_path, hash_file_name))
            dst_path = os.path.join(backup_path, hash_file_name)

            # copy
            try:
                shutil.copyfile(src_path, dst_path)
            except Exception as e:
                logging.error("[backup] copy %s failed, err=%s", hash_file_name, e)
                space.send_ws(name="backup", msg_type="msg", status="run", data={
                    "msg": f"src_path: {src_path}, dst_path: {dst_path}"
                })
                continue

            if i % msg_interval == 0:
                space.send_ws(name="backup", msg_type="sync", status="run", data={
                    "now": i, "total": attr_len
                })

        space.send_ws(name="backup", msg_type="done", status="success", data={
            "total": attr_len
        })
        self.write_json(status="success", data=attr_len)
        return
