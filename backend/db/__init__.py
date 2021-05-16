from backend import config
from db import mysqldriver
from db.driver import Driver

options = config.get_options()
DB_TYPE = options.db_type


def new_driver(workspace) -> Driver:
    driver = None
    if DB_TYPE == "mysql":
        driver = mysqldriver.MySQLDriver(options, workspace)
    else:
        print("Db type %s is not supported" % DB_TYPE)
    return driver
