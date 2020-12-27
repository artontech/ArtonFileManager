import logging

from tornado.ioloop import IOLoop

import config
import router

if __name__ == "__main__":
    logging.info("App start")
    options = config.get_options()
    app = router.make_app()

    port = options.http_port
    logging.info("HTTP server start at %d" % (port))
    app.listen(port)
    IOLoop.current().start()