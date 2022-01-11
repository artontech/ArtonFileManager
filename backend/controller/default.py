''' default '''
import asyncio
import json
import logging

from concurrent.futures import ThreadPoolExecutor
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.web import (
    _ARG_DEFAULT,
    RequestHandler,
    MissingArgumentError
)
from tornado.websocket import WebSocketHandler

from backend import config
from backend.util import (
    jsonencoder
)

class DefaultHandler(RequestHandler):
    ''' default '''
    args = None

    # See: https://github.com/tornadoweb/tornado/issues/2531
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    executor = ThreadPoolExecutor(20)

    def data_received(self, chunk):
        pass

    def initialize(self, name="name"):
        ''' initialize '''
        self.name = name
        self.options = config.get_options()

    def prepare(self):
        ''' prepare '''
        if "OPTIONS" == self.request.method.upper():
            self.set_status(204)
            self.set_default_headers()
            self.finish()
            return

        content_type = self.request.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            data = bytes.decode(self.request.body)
            self.args = json.loads(data, strict=False)
        logging.debug("Access:%s,content:%s,data:%s",
                      self.name, content_type, self.args)

    def set_default_headers(self):
        ''' set_default_headers '''
        self.set_header("Content-Type", "application/json; charset=utf-8")

        origin = self.request.headers.get("Origin")
        if origin is None or origin == "":
            origin = "*"
        self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header("Access-Control-Allow-Methods",
                        "GET, POST, HEAD, TRACE, PUT, DELETE, OPTIONS, CONNECT")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type, x_requested_with, Token, *")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Max-Age", "3600")

    def get_arg(self, name: str, default=_ARG_DEFAULT, strip: bool = True):
        ''' 
        If default is not provided, the argument is considered to be
        required, and we raise a `MissingArgumentError` if it is missing.
        '''
        if self.args is not None:
            if name in self.args:
                return self.args.get(name, default)
        try:
            return self.get_argument(name, default, strip)
        except MissingArgumentError as e:
            # self.write_json(err="miss_arg", data={"name": name})
            raise e

    def write_json(self, status="fail", err="", data=None, status_code=200):
        ''' write_json '''
        result = {"status": status, "err": err, "data": data}
        self.write(json.dumps(result, cls=jsonencoder.DefaultEncoder))
        if status_code != 200:
            self.set_status(status_code, reason=err)


class DefaultWSHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def write_json(self, msg_type="none", status="fail", err="", data=None):
        ''' write_json '''
        result = {"type": msg_type, "status": status, "err": err, "data": data}
        self.write_message(json.dumps(result, cls=jsonencoder.DefaultEncoder))
