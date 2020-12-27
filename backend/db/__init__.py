from backend import config
from db import redisdriver, mysqldriver
from db.driver import Driver

options = config.get_options()
DB_TYPE = options.db_type


def new_driver(workspace) -> Driver:
    driver = None
    if DB_TYPE == "redis":
        driver = redisdriver.RedisDriver(options, workspace)
    elif DB_TYPE == "mysql":
        driver = mysqldriver.MySQLDriver(options, workspace)
    return driver
