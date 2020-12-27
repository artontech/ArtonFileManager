import logging, os, signal, subprocess

import redis

from db.driver import Driver

class RedisDriver(Driver):
    def __init__(self, options, workspace):
        self.options = options
        self.workspace = workspace

        self.path = self.options.redis_path
        self.pool = None
        self.pid = None

    def open(self):
        cmd = [os.path.join(self.path, "redis-server.exe"), os.path.join(self.workspace, "redis.windows.conf")]
        logging.info("Redis path: %s" % (self.path))
        ret = subprocess.Popen(cmd)
        self.pid = ret.pid

        self.pool = redis.ConnectionPool(host = "127.0.0.1", port = 13311, decode_responses = True)
        conn = redis.Redis(connection_pool = self.pool)
        workspace_old = conn.getset("workspace", self.workspace)
        conn.close()
        is_new = workspace_old != self.workspace
        logging.info("workspace_old=%s, workspace=%s, is_new=%s" % (workspace_old, self.workspace, is_new))

        return self.pid != None

    def close(self):
        result = False

        conn = redis.Redis(connection_pool = self.pool)
        conn.save()
        conn.close()
        
        try:
            ret = os.kill(self.pid, signal.SIGINT)
            logging.info("Redis close, killed pid %s, returns %s" % (self.pid, ret))
            result = True
        except Exception:
            result = False
        
        return result