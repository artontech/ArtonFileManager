''' OSS '''
import json
import logging
import os
import time

import oss2
import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.model.oss import OSS
from backend.service import workspace
from backend.util import fileio

MAX_RETRY = 3
OSS_MULTIPART_THRESHOLD = 10 * 1024 * 1024
OSS_NUM_THREADS = 10

class OssWebSocket(DefaultWSHandler):
    name = "oss"

    def open(self):
        logging.info("[ws] OSS WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            wid = msg_json.get("wid", None)
            logging.info("[ws] oss init: wid=%s", wid)
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


class Sync(DefaultHandler):
    ''' sync '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get netdisk info
        netdisks = space.driver.get_netdisks(type_name="oss")
        if netdisks is None:
            self.write_json(err="db")
            return
        if len(netdisks) < 1:
            self.write_json(err="no_netdisk")
            return
        netdisk_info = netdisks[0]

        bucket = oss2.Bucket(oss2.Auth(netdisk_info.api_key, netdisk_info.secret_key), 
            netdisk_info.redirect_uri, netdisk_info.upload_root)

        yield self.sync(space, bucket)

    @run_on_executor
    def sync(self, space, bucket):
        # get attributes
        attrs = space.driver.union_attribute_oss()
        if attrs is None:
            self.write_json(err="db")
            return
        attr_len = len(attrs)
        space.send_ws(name="oss", msg_type="check", status="success", data={
            "total": attr_len
        })

        last_err = ""
        msg_interval = min(1000, max(1, int(attr_len / 1000)))
        if msg_interval <= 0:
            msg_interval = 1
        for i in range(attr_len):
            retry = 0
            while retry < MAX_RETRY:
                if retry > 3:
                    time.sleep(360)
                elif retry > 0:
                    time.sleep(36)
                retry += 1
                attr = attrs[i]
                hash_file_name = fileio.format_file_name(
                    attr.size, attr.crc32, attr.sha256, None)
                target_path = os.path.abspath(
                    os.path.join(space.data_path, hash_file_name))
                upload_path = 'afm/%s' % (hash_file_name)

                # upload
                try:
                    put_obj_result = oss2.resumable_upload(bucket, upload_path, target_path, 
                        multipart_threshold=OSS_MULTIPART_THRESHOLD, num_threads=OSS_NUM_THREADS)
                    if str(put_obj_result.status) != "200":
                        last_err = "upload_status"
                        continue
                except Exception as e:
                    last_err = "upload_fail"
                    logging.error("[oss] upload %s failed, err=%s", hash_file_name, e)
                    #logging.info(traceback.format_exc())
                    continue

                # add oss
                oss = OSS()
                oss.id = attr.id
                oss.attribute = attr.id
                oss.path = upload_path
                oss.id, ok = space.driver.add_oss(oss)
                if not ok:
                    last_err = "db"
                    continue
                space.driver.commit()

                if i % msg_interval == 0:
                    space.send_ws(name="oss", msg_type="sync", status="run", data={
                        "now": i, "total": attr_len
                    })

                # Stop retry
                retry = 0
                break
            if retry >= MAX_RETRY:
                logging.warning("[oss] Sync attr %s failed, err=%s", attr.id, last_err)
                with open("./failed_file.log", 'a+') as fout:
                    fout.write(target_path + '\n')
                continue

        space.send_ws(name="oss", msg_type="done", status="success", data={
            "total": attr_len
        })
        self.write_json(status="success", data=attr_len)
        return