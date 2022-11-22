''' Search File '''
import json
import logging

import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.model.file import File
from backend.service import workspace

class SearchFileWebSocket(DefaultWSHandler):
    name = "searchfile"

    def open(self):
        logging.info("[ws] Search File WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            wid = msg_json.get("wid", None)
            logging.info("[ws] searchfile init: wid=%s", wid)
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


class Search(DefaultHandler):
    ''' search '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        attr_id = self.get_arg("attr_id", default=None)
        ahash = self.get_arg("ahash", default=None)
        dhash = self.get_arg("dhash", default=None)
        phash = self.get_arg("phash", default=None)

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        if attr_id is not None:
            yield self.search_attr(space, attr_id)
        elif ahash is not None or dhash is not None or phash is not None:
            yield self.search_hash(space, ahash, dhash, phash)
        else:
            self.write_json(err="unknown_args")

    def get_files(self, space, attr_id):
        file_model = File()
        file_model.none()
        file_model.attribute = attr_id
        file_model.delete = 0
        file_list, _ = space.driver.get_files(file_model)
        return file_list

    @run_on_executor
    def search_attr(self, space, attr_id):
        self.write_json(status="success", data=self.get_files(space, attr_id))

    @run_on_executor
    def search_hash(self, space, ahash, dhash, phash):
        # TODO: search hash by hamming distance
        attrs = space.driver.get_attrs(ahash=ahash, dhash=dhash, phash=phash)
        if attrs is None:
            self.write_json(err="db", status_code=500)
            return

        result_list = []
        for attr in attrs:
            file_list = self.get_files(space, attr.id)
            result_list.extend(file_list)

        self.write_json(status="success", data=result_list)
