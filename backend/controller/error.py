''' 404 '''

from tornado.web import RequestHandler


class NotFound(RequestHandler):
    ''' 404 '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.write("404")
        self.set_status(404, reason="not found")
