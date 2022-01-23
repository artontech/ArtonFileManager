''' Workspace '''
import logging
import os
import shutil

from backend import db
from backend.controller.default import DefaultHandler
from backend.service import workspace


class Ping(DefaultHandler):
    ''' ping '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        self.write_json(status="success")


class Init(DefaultHandler):
    ''' init '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        path = self.get_arg("path")
        password = self.get_arg("password")

        driver = db.new_driver(path, password)
        ret = driver.init()
        if ret != 0:
            self.write_json(err="init", data={"returncode": ret})
            return

        self.write_json(status="success")


class Open(DefaultHandler):
    ''' open '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        path = self.get_arg("path")

        if workspace.contains_path(path):
            space = workspace.get_by_path(path)
            logging.info("Workspace exist: %s" % (space.serializable()))
        else:
            space = workspace.add(path)

        if space.enabled:
            self.write_json(status="success", data=space.serializable())
        else:
            self.write_json(err="failed", data=space.serializable())


class Close(DefaultHandler):
    ''' close '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        '''post '''
        wid = self.get_arg("wid")
        path = self.get_arg("path")

        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            space = workspace.get_by_path(path)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        try:
            # stop db
            if not space.driver.close():
                self.write_json(err="close_fail")
                return

            # remove temp files
            tmp_path = os.path.join(self.options.static_path, "tmp")
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)

            self.write_json(status="success")
        finally:
            workspace.del_by_id(wid)
            workspace.del_by_path(path)
            
