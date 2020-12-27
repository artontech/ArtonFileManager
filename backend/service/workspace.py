''' workspace service '''

import json
import logging
import os

from backend import db

if not "PATH_MAP" in dir():
    PATH_MAP = {}
    ID_MAP = {}


class WorkSpace():
    ''' workspce '''

    def __init__(self, path):
        self.wid = id(self)
        self.err = None
        self.path = path
        self.ws_list = []

        # load json config
        JSON_PATH = os.path.join(path, "afm_config.json")
        with open(JSON_PATH, 'r+') as f:
            config_json = json.load(f)
        self.data_path = config_json.get("data_path")
        os.makedirs(self.data_path, exist_ok=True)

        self.driver = db.new_driver(path)
        success = self.driver.open()
        if not success:
            self.enabled = False
            self.err = "no_pid"
            return

        self.enabled = True

    def serializable(self):
        ''' to serializable '''
        result = {
            "wid": self.wid,
            "enabled": self.enabled,
            "err": self.err,
            "path": self.path,
            "ws_count": len(self.ws_list)
        }
        return result

    def to_string(self):
        ''' to string '''
        return json.dumps(self.serializable())

    def add_ws(self, ws):
        self.ws_list.append(ws)

    def del_ws(self, ws):
        new_list = []
        for w in self.ws_list:
            if w != ws:
                new_list.append(w)
        self.ws_list = new_list

    def send_ws(self, msg_type="none", status="fail", err="", data=None):
        for w in self.ws_list:
            w.write_json(msg_type, status, err, data)


def contains_path(path):
    ''' find path '''
    return PATH_MAP.__contains__(os.path.abspath(path))


def contains_id(i):
    ''' find id '''
    return ID_MAP.__contains__(i)


def get_by_path(path) -> WorkSpace:
    ''' get by path '''
    logging.info("Get workspace %s" % path)
    return PATH_MAP.get(os.path.abspath(path), None)


def get_by_id(i) -> WorkSpace:
    ''' get by id '''
    logging.info("Get workspace %s" % i)
    return ID_MAP.get(int(i), None)


def del_by_path(path):
    ''' del by path '''
    space = PATH_MAP.get(os.path.abspath(path), None)
    if space is None:
        return
    i = space.wid
    del PATH_MAP[path]
    del ID_MAP[i]


def del_by_id(i):
    ''' del by id '''
    space = ID_MAP.get(i, None)
    if space is None:
        return
    path = space.path
    del PATH_MAP[path]
    del ID_MAP[i]


def add(path):
    ''' add workspace '''
    space = WorkSpace(path)
    if space.enabled:
        PATH_MAP[path] = space
        ID_MAP[space.wid] = space
    return space
