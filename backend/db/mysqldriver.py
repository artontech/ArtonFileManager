''' mysql driver '''

import configparser
import datetime
import json
import logging
import os
import subprocess
import sys
import threading
import time

import pymysql

from db.driver import Driver
from backend.model.default import DefaultModel
from backend.model.attribute import (
    Attribute,
    get_attribute_list,
    union_attribute_baidunetdisk_list,
    union_attribute_oss_list
)
from backend.model.dir import (
    Dir,
    get_dir_list
)
from backend.model.file import (
    File,
    get_file_list
)
from backend.model.attributetag import (
    AttributeTag,
    get_attribute_tag_list,
    union_attribute_tag_list
)
from backend.model.tag import (
    Tag,
    get_tag_list
)
from backend.model.netdisk import (
    Netdisk,
    get_netdisk_list
)
from backend.model.baidunetdisk import (
    BaiduNetdisk,
    get_baidunetdisk_list
)
from backend.model.oss import (
    OSS,
    get_oss_list
)
from backend.util import (
    fileio
)


def safe(data: str, collate: bool = False) -> str:
    ''' escape string for sql '''
    result = "'%s'" % pymysql.escape_string(data)
    if collate:
        result += " COLLATE utf8mb4_general_ci"
    return result


def mylock(func):
    ''' lock since pymysql not support async call '''

    def wrapper(self, *args, **kwargs):
        self.lock()
        result = func(self, *args, **kwargs)
        self.unlock()
        return result
    return wrapper


class MySQLDriver(Driver):
    ''' MySQLDriver '''

    def __init__(self, options, workspace: str, password: str=None):
        self.database = None
        self.db = None
        self.db_name = r"arton_file_manager"
        self.host = None
        if sys.platform == 'win32':
            self.json_path = os.path.join(workspace, "afm_config.json")
        elif sys.platform == 'linux':
            self.json_path = os.path.join(workspace, "afm_config_linux.json")
        self.config_json = {}
        self.options = options
        self.password = password
        self.port = None
        self.user = None
        self.workspace = workspace
        self._lock = threading.Lock()

    def lock(self):
        ''' acquire lock '''
        self._lock.acquire(blocking=True, timeout=-1)

    def unlock(self):
        ''' release lock '''
        if self._lock.locked():
            self._lock.release()

    def init(self):
        ''' init '''
        logging.info("Init mysql at: %s", self.options.mysql_path)

        if os.path.exists(self.json_path):
            logging.warning("Workspace already exist: %s", self.workspace)
            return 0

        os.makedirs(self.workspace, exist_ok=True)

        # add json config
        config_json = {
            "workspace": self.workspace,
            "data_path": os.path.join(self.workspace, "afm_data")
        }
        with open(self.json_path, 'w+') as fin:
            json.dump(config_json, fin)

        os.makedirs(os.path.join(self.workspace, "mysql/data"))

        if sys.platform == 'win32':
            return self.init_win()
        elif sys.platform == 'linux':
            return self.init_docker()

        print("unknown platform", sys.platform)
        return -1

    def init_win(self):
        # gen config
        mysql_path = self.options.mysql_path
        config_path = self.options.config_path

        # replace settings content
        ini_src_path = os.path.join(config_path, "mysql.windows.ini")
        ini_dst_path = os.path.join(self.workspace, "mysql.windows.ini")
        fileio.replace_file_content(
            ini_src_path,
            ini_dst_path,
            [
                (r"%port%", "13311"),
                (r"%workspace%", self.workspace.replace("\\", "/")),
                (r"%mysql%", os.path.dirname(mysql_path).replace("\\", "/"))
            ]
        )

        # replace sql content
        sql_db_path = os.path.join(config_path, "%s.sql" % (self.db_name))
        db_structure = fileio.read_text_file(sql_db_path)
        sql_src_path = os.path.join(config_path, "mysql.windows.sql")
        sql_dst_path = os.path.join(self.workspace, "mysql.windows.sql")
        fileio.replace_file_content(
            sql_src_path,
            sql_dst_path,
            [
                (r"%password%", self.password),
                (r"%db_name%", self.db_name),
                (r"%db_structure%", db_structure)
            ]
        )

        # init service
        cmd = [os.path.join(mysql_path, "mysqld"),
               "--defaults-file=%s" % (ini_dst_path),
               "--init-file=%s" % (sql_dst_path),
               "--initialize"]  # --initialize-insecure
        ret = subprocess.run(cmd, check=False)
        return ret.returncode

    def init_docker(self):
        ''' init mysql in docker image '''
        print("init mysql in linux is not support")
        return -1

    def open(self):
        # load config
        if not os.path.exists(self.json_path):
            logging.warning("No json config: %s", self.workspace)
            return -1
        with open(self.json_path, 'r+') as f:
            config_json = json.load(f)
            self.config_json = config_json
        self.host = config_json.get("host", "localhost")
        self.user = config_json.get("user", "root")
        self.password = config_json.get("password", "")
        self.database = config_json.get("database", "arton_file_manager")
        self.port = config_json.get("port", 13311)

        if sys.platform == 'win32':
            return self.open_win()
        elif sys.platform == 'linux':
            return self.open_docker()

        print("unknown platform", sys.platform)
        return -1

    def open_win(self):
        mysql_path = self.options.mysql_path
        ini_path = os.path.join(self.workspace, "mysql.windows.ini")
        logging.info("Open mysql at: %s", mysql_path)

        # if workspace changed, fix mysql
        last_workspace = self.config_json.get("workspace", self.workspace)
        if os.path.abspath(last_workspace) != os.path.abspath(self.workspace):
            logging.info("Workspace changed, fix mysql...")
            mysql_path = os.path.join(self.workspace, "mysql")
            for fn in os.listdir(mysql_path):
                fpath = os.path.join(mysql_path, fn)
                if os.path.isfile(fpath) and fn.startswith("mysql-bin"):
                    os.remove(fpath)

            # update ini
            config = configparser.ConfigParser()
            config.read(ini_path)
            mysql_path = mysql_path.replace("\\", "/")  # for mysql
            sock_path = mysql_path + "/mysql.sock"
            config.set("client", "socket", sock_path)
            config.set("mysqld", "socket", sock_path)
            config.set("mysqld", "datadir", mysql_path + "/data")
            config.set("mysqld", "log-bin", mysql_path + "/mysql-bin")
            config.set("mysqld", "relay-log", mysql_path + "/relay-log")
            config.set("mysqld_safe", "log-error",
                       mysql_path + "/mysql.coco.err")
            config.set("mysqld_safe", "pid-file", mysql_path + "/mysql.pid")
            with open(ini_path, "w+") as f:
                config.write(f)

            # update workspace to json
            self.config_json["workspace"] = self.workspace
            with open(self.json_path, 'w+') as f:
                json.dump(self.config_json, f)

        cmd = [os.path.join(mysql_path, "mysqld"),
               "--install", "ArtonFileManagerMySQL",
               "--defaults-file=%s" % (ini_path)]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            return ret

        cmd = ["net", "start", "ArtonFileManagerMySQL"]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            return ret

        if self.open_db() is None:
            ret.returncode = -99
            return ret

        return ret

    def open_docker(self):
        ''' open mysql in docker image '''
        conf_path = os.path.join(self.workspace, "mysql.cnf")
        os.chmod(conf_path, 0o0644)
        cmd = [
            "docker", "run",
            "--name", "afm-mysql",
            "-v", "%s:/data" % (self.workspace),
            "-v", "%s:/etc/mysql/conf.d/mysql.cnf:ro" % (conf_path),
            "--user", "1000:1000",
            "-p", "%s:%s" % (self.port, self.port),
            "-e", "MYSQL_ROOT_PASSWORD=afm_root",
            "-d", "mysql:8.0"
            ]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            return ret

        retry = 0
        while retry < 10:
            try:
                time.sleep(2)
                if self.open_db() is not None:
                    return ret
            except pymysql.err.OperationalError as err:
                logging.info("retry connecting mysql")
                if retry >= 9:
                    raise err
        ret.returncode = -99
        return ret

    def close(self):
        self.close_db()

        if sys.platform == 'win32':
            return self.close_win()
        elif sys.platform == 'linux':
            return self.close_docker()

        print("unknown platform", sys.platform)
        return False

    def close_win(self):
        result = True

        cmd = ["net", "stop", "ArtonFileManagerMySQL"]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            result = False

        cmd = ["sc", "delete", "ArtonFileManagerMySQL"]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            result = False

        return result

    def close_docker(self):
        result = True

        cmd = ["docker", "stop", "/afm-mysql"]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            result = False

        cmd = ["docker", "rm", "/afm-mysql"]
        ret = subprocess.run(cmd, check=False)
        if ret.returncode != 0:
            result = False

        return result

    @mylock
    def commit(self):
        ''' commit '''
        self.open_db().commit()
        self.close_db()

    def rollback(self):
        ''' rollback '''
        self.open_db().rollback()

    def open_db(self):
        ''' open db connection '''
        if self.db is None:
            self.db = pymysql.connect(host=self.host,
                                      user=self.user, password=self.password,
                                      database=self.database, port=self.port)
        return self.db

    def close_db(self):
        ''' close db connection '''
        if self.db is not None:
            try:
                self.db.close()
                self.db = None
            except Exception as err:
                logging.info("close fail: %s", err)

    def get_a_row(self, table: str):
        ''' get one row '''

        result = None
        sql = "SELECT * FROM `%s` limit 0, 1" % (table)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                if len(results) > 0:
                    result = results[0]
        except Exception as err:
            logging.warning(sql)
            raise err

        return result

    def page(self, table: str, model: DefaultModel, sql_where: str) -> str:
        ''' page '''
        sql = "SELECT * FROM `%s`.`%s`" % (self.db_name, table)
        if model.do_page():
            start_id = (model.page_no - 1) * model.page_size
            sql += " WHERE %s and id>=(SELECT id FROM `%s` WHERE %s LIMIT %d,1) LIMIT %d" % (
                sql_where, table, sql_where, start_id, model.page_size)
        else:
            sql += " WHERE %s" % (sql_where)
        return sql

    def total(self, table: str, sql_where: str) -> str:
        ''' total '''
        sql = "SELECT count(0) FROM `%s`.`%s` WHERE %s" % (
            self.db_name, table, sql_where)
        return sql

    def table_size(self, table: str, sql_where: str = "") -> int:
        try:
            sql = f"SELECT count(0) FROM `{self.db_name}`.`{table}` {sql_where}"
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                count = cursor.fetchone()[0]
        except Exception as err:
            logging.warning(sql)
            raise err
        return count

    def get_dir_file_list(self, db_results):
        ''' get dir file list '''
        result = []
        if db_results is None or len(db_results) <= 0:
            return result

        for row in db_results:
            obj_type = row[0]
            obj = None
            if obj_type == "dir":
                obj = Dir()
                obj.parent = row[2]
            elif obj_type == "file":
                obj = File()
                obj.dir = row[2]
                obj.attribute = row[3]
                obj.ext = row[5]
            else:
                logging.error("[list] unknown type %s", obj_type)
                continue
            obj.id = row[1]
            obj.type = obj_type
            obj.name = row[4]
            result.append(obj)
        return result

    def reset_auto_increment(self, table: str):
        ''' reset auto_increment '''

        result = None
        sql = "ALTER TABLE `%s` auto_increment = 1" % table

        try:
            with self.open_db().cursor() as cursor:
                result = cursor.execute(sql)
        except Exception as err:
            logging.warning(sql)
            raise err

        return result

    @mylock
    def get_miss_ids(self, table: str, limit: int = None) -> list:
        ''' get id gap '''

        result = []
        # reset auto_increment if table is empty
        if self.get_a_row(table) is None:
            self.reset_auto_increment(table)
            self.open_db().commit()
            self.close_db()
            return result

        # for MySQL 8.0+
        sql = "SELECT `query`.`id`, `query`.`flag` FROM (\
SELECT row_number() over (ORDER BY t.id) As `id`, \
IF (row_number() over (ORDER BY t.id) = t.id, 0, 1) AS `flag` \
FROM `%s` t ORDER BY t.id) AS `query` \
WHERE `query`.`flag` != 0 AND NOT EXISTS (SELECT id FROM `%s` WHERE id = `query`.`id`)" % (table, table)

        if limit is not None:
            sql += " LIMIT 0,%d" % (limit)

        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                result = [r[0] for r in results]
        except Exception as err:
            logging.warning(sql)
            raise err

        return result

    def get_miss_id(self, table: str) -> list:
        ''' get missing id '''
        result = None
        results = self.get_miss_ids(table, 1)
        if len(results) > 0:
            result = results[0]
        return result

    @mylock
    def delete(self, table: str, item_id: str) -> bool:
        ''' delete by id '''

        ok = False
        sql = "DELETE FROM `%s` WHERE `id`=%s" % (table, item_id)
        try:
            with self.open_db().cursor() as cursor:
                r = cursor.execute(sql)
                ok = r > 0
        except Exception as err:
            logging.warning(sql)
            raise err

        return ok

    @mylock
    def add_file(self, file: File) -> bool:
        ''' add file '''
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ok = True

        if file.id is None:
            item_id = "NULL"
        else:
            item_id = "'%s'" % file.id
        if file.name is None:
            name = "NULL"
        else:
            name = "%s" % safe(file.name)
        if file.ext is None:
            ext = "NULL"
        else:
            ext = "%s" % safe(file.ext)

        sql = "INSERT INTO `%s`.file (`id`,`dir`,`attribute`,`name`,`ext`,`delete`,`createtime`,`modtime`) \
            VALUES (%s,%s,NULL,%s,%s,0,'%s','%s');" % (self.db_name, item_id, file.dir, name, ext, time_now, time_now)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = cursor.lastrowid
        except Exception as err:
            logging.warning(sql)
            ok = False
            self.rollback()
            raise err

        return current_id, ok

    @mylock
    def add_dir(self, dir_model: Dir):
        ''' add new dir to database '''
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_id = 0
        ok = False

        if dir_model.id is None:
            item_id = "NULL"
        else:
            item_id = "'%s'" % dir_model.id
        if dir_model.parent is None:
            parent = 0
        else:
            parent = "%d" % dir_model.parent
        if dir_model.name is None:
            name = "NULL"
        else:
            name = "%s" % safe(dir_model.name)

        sql = "INSERT INTO `%s`.dir (`id`,`parent`,`name`,`delete`,`createtime`,`modtime`) VALUES \
            (%s,%s,%s,0,'%s','%s');" % (self.db_name, item_id, parent, name, time_now, time_now)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = int(cursor.lastrowid)
                ok = True
        except Exception as err:
            logging.warning(sql)
            self.rollback()
            raise err
        return current_id, ok

    @mylock
    def add_attribute(self, attr: Attribute):
        ''' add new attr to database '''
        current_id = "NULL"
        ok = False

        item_id = "NULL" if attr.id is None else f"'{attr.id}'"
        encrypt_crc32 = "NULL" if attr.encrypt_crc32 is None else f"'{attr.encrypt_crc32}'"
        encrypt = "NULL" if attr.encrypt is None else f"'{attr.encrypt}'"
        key = "NULL" if attr.key is None else f"'{attr.key}'"
        check_date = "NULL" if attr.check_date is None else f"'{attr.check_date}'"

        sql = f"INSERT INTO `{self.db_name}`.attribute (\
`id`,`file`,`type`,`size`,`encrypt_crc32`,`crc32`,`sha256`,`ext`,`width`,`height`,`color`, \
`ahash`,`phash`,`dhash`,`desc`,`encrypt`,`key`,`delete`,`check_date`) VALUES (\
{item_id},{attr.file},{attr.type},{attr.size},{encrypt_crc32},'{attr.crc32}',\
'{attr.sha256}',{safe(attr.ext)},{attr.width},{attr.height},'{attr.color}',\
'{attr.ahash}','{attr.phash}','{attr.dhash}',{safe(attr.desc)},{encrypt},{key},\
{attr.delete},{check_date});"
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = cursor.lastrowid
                ok = True
        except Exception as err:
            logging.warning(sql)
            self.rollback()
            raise err
        return current_id, ok

    @mylock
    def add_attribute_tag(self, attribute_tag: AttributeTag):
        ''' add new attribute tag to database '''
        current_id = "NULL"
        ok = False

        if attribute_tag.id is None:
            item_id = "NULL"
        else:
            item_id = "'%s'" % attribute_tag.id

        sql = "INSERT INTO `%s`.attribute_tag (`id`,`tag_id`,`target`,`type`,`delete`) VALUES (%s,%d,%d,%d,0);" % (
            self.db_name, item_id, attribute_tag.tag_id, attribute_tag.target, attribute_tag.type)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = cursor.lastrowid
                ok = True
        except Exception as err:
            logging.warning(sql)
            self.rollback()
            raise err
        return current_id, ok

    @mylock
    def add_tag(self, tag: Tag):
        ''' add new tag to database '''
        current_id = "NULL"
        ok = False

        if tag.id is None:
            item_id = "NULL"
        else:
            item_id = "'%s'" % tag.id

        sql = "INSERT INTO `%s`.tag (`id`,`key`,`value`,`delete`) VALUES (%s,%s,%s,0);" % (
            self.db_name, item_id, safe(tag.key), safe(tag.value))
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = cursor.lastrowid
                ok = True
        except Exception as err:
            logging.warning(sql)
            self.rollback()
            raise err
        return current_id, ok

    @mylock
    def add_baidunetdisk(self, baidunetdisk: BaiduNetdisk):
        ''' add baidu netdisk file info '''
        current_id = "NULL"
        ok = False

        if baidunetdisk.id is None:
            item_id = "NULL"
        else:
            item_id = "'%s'" % baidunetdisk.id

        sql = "INSERT INTO `%s`.baidunetdisk (`id`,`attribute`,`fs_id`) VALUES (%s,%d,%d);" % (
            self.db_name, item_id, baidunetdisk.attribute, baidunetdisk.fs_id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = cursor.lastrowid
                ok = True
        except Exception as err:
            logging.warning(sql)
            self.rollback()
            raise err
        return current_id, ok

    @mylock
    def add_oss(self, oss: OSS):
        ''' add baidu netdisk file info '''
        current_id = "NULL"
        ok = False

        if oss.id is None:
            item_id = "NULL"
        else:
            item_id = "'%s'" % oss.id

        sql = "INSERT INTO `%s`.oss (`id`,`attribute`,`path`) VALUES (%s,%d,%s);" % (
            self.db_name, item_id, oss.attribute, safe(oss.path))
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                current_id = cursor.lastrowid
                ok = True
        except Exception as err:
            logging.warning(sql)
            self.rollback()
            raise err
        return current_id, ok

    @mylock
    def get_files(self, file: File, attr_null: bool = None):
        ''' list files '''
        results = []
        count = None

        sql_where = ""
        if file.id is not None:
            sql_where += " and `id`=%s" % (file.id)
        if attr_null is not None:
            if attr_null:
                sql_where += " and `attribute` is NULL"
            else:
                sql_where += " and `attribute` is not NULL"
        elif file.attribute is not None:
            sql_where += " and `attribute`=%d" % (file.attribute)
        if file.delete is not None:
            sql_where += " and `delete`=%d" % (file.delete)
        if file.dir is not None:
            sql_where += " and `dir`=%d" % (file.dir)
        if file.name is not None:
            sql_where += " and `name`=%s" % safe(file.name)
        if file.ext is not None:
            sql_where += " and `ext`=%s" % safe(file.ext)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = self.page("file", file, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_file_list(cursor.fetchall())
                if file.do_page():
                    sql = self.total("file", sql_where)
                    cursor.execute(sql)
                    count = cursor.fetchone()[0]
        except Exception as err:
            logging.warning(sql)
            raise err
        return results, count

    @mylock
    def get_dirs(self, item_id=None, parent: int = None, delete: int = None, name: str = None):
        ''' list dirs '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if parent is not None:
            sql_where += " and `parent`=%d" % (parent)
        if delete is not None:
            sql_where += " and `delete`=%d" % (delete)
        if name is not None:
            sql_where += " and `name`=%s" % safe(name)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.dir WHERE %s" % (self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_dir_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_attrs(
            self,
            item_id=None,
            size: int = None,
            crc32: int = None,
            sha256: str = None,
            ahash: int = None,
            dhash: int = None,
            phash: int = None,
            delete: int = 0,
            check_date: str = None
        ):
        ''' list attributes '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if size is not None:
            sql_where += " and `size`=%d" % (size)
        if crc32 is not None:
            sql_where += " and `crc32`=%d" % (crc32)
        if sha256 is not None:
            sql_where += " and `sha256`='%s'" % (sha256)
        if ahash is not None:
            sql_where += " and `ahash`='%s'" % (ahash)
        if dhash is not None:
            sql_where += " and `dhash`='%s'" % (dhash)
        if phash is not None:
            sql_where += " and `phash`='%s'" % (phash)
        if delete is not None:
            sql_where += " and `delete`=%d" % (delete)
        if check_date is not None:
            sql_where += " and (`check_date` is NULL or `check_date`<%s)" % (safe(check_date))
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.attribute WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_attribute_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_attr_hashes(
            self,
            delete: int = 0
        ):
        ''' list attribute hashes '''
        results = []

        sql_where = ""
        if delete is not None:
            sql_where += " and `delete`=%d" % (delete)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT id,ahash,dhash,phash FROM `%s`.attribute WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = []
                for row in cursor.fetchall():
                    obj = Attribute()
                    obj.id = row[0]
                    obj.ahash = row[1]
                    obj.dhash = row[2]
                    obj.phash = row[3]
                    results.append(obj)
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_attribute_tags(self, item_id=None, tag_id: int = None, target: int = None, type_id: int = None, delete: int = 0):
        ''' list attribute tags '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if tag_id is not None:
            sql_where += " and `tag_id`=%d" % (tag_id)
        if target is not None:
            sql_where += " and `target`=%d" % (target)
        if type_id is not None:
            sql_where += " and `type`=%d" % (type_id)
        if delete is not None:
            sql_where += " and `delete`=%d" % (delete)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.attribute_tag WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_attribute_tag_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_baidunetdisks(self, item_id=None, attribute: int = None):
        ''' list baidunetdisk '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if attribute is not None:
            sql_where += " and `attribute`=%d" % (attribute)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.baidunetdisk WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_baidunetdisk_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_oss(self, item_id=None, attribute: int = None):
        ''' list oss '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if attribute is not None:
            sql_where += " and `attribute`=%d" % (attribute)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.oss WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_oss_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_tags(self, item_id=None, key: str = None, value: str = None, delete: int = 0):
        ''' list tags '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if key is not None:
            sql_where += " and `key`=%s" % safe(key)
        if value is not None:
            sql_where += " and `value`=%s" % safe(value)
        if delete is not None:
            sql_where += " and `delete`=%d" % (delete)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.tag WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_tag_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_netdisks(self, item_id=None, type_name: str = None):
        ''' list tags '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `id`=%s" % (item_id)
        if type_name is not None:
            sql_where += " and `type`=%s" % safe(type_name)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT * FROM `%s`.netdisk WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = get_netdisk_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def union_attribute_tags(self, item_id=None, target: int = None, type_id: int = None, delete: int = 0):
        ''' list union attribute tags '''
        results = []

        sql_where = ""
        if item_id is not None:
            sql_where += " and `at`.`id`=%s" % (item_id)
        if target is not None:
            sql_where += " and `at`.`target`=%d" % (target)
        if type_id is not None:
            sql_where += " and `at`.`type`=%d" % (type_id)
        if delete is not None:
            sql_where += " and `at`.`delete`=%d" % (delete)
        sql_where = sql_where.strip().lstrip('and')
        if sql_where == "":
            return results

        sql = "SELECT `at`.*, `t`.`key`, `t`.`value` FROM `%s`.attribute_tag `at` INNER JOIN `%s`.tag `t` ON %s AND `at`.tag_id=`t`.id" % (
            self.db_name, self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = union_attribute_tag_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def union_attribute_baidunetdisks(self):
        ''' list attributes not uploaded '''
        results = []

        sql = "SELECT a.id,a.size,a.crc32,a.sha256,b.fs_id FROM `%s`.attribute a LEFT JOIN `%s`.baidunetdisk b ON a.id=b.attribute WHERE b.attribute is null" % (
            self.db_name, self.db_name)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = union_attribute_baidunetdisk_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def union_attribute_oss(self):
        ''' list oss not uploaded '''
        results = []

        sql = "SELECT a.id,a.size,a.crc32,a.sha256,b.path FROM `%s`.attribute a LEFT JOIN `%s`.oss b ON a.id=b.attribute WHERE b.attribute is null" % (
            self.db_name, self.db_name)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = union_attribute_oss_list(cursor.fetchall())
        except Exception as e:
            logging.warning(sql)
            raise e
        return results

    @mylock
    def get_dirs_files(self, current: int, page_no: int = None, page_size: int = None):
        ''' list files and dirs '''
        results = []
        count = None

        sql = "SELECT 'dir', id, parent, null, `name`, null FROM dir WHERE `parent`=%d and `delete`=0" % (
            current)
        sql += " UNION SELECT 'file', id, dir, attribute, `name`, ext FROM file WHERE dir=%d and `delete`=0" % (
            current)
        if page_no is not None and page_size is not None:
            start_id = (page_no - 1) * page_size
            sql += " LIMIT %d, %d" % (start_id, page_size)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                results = self.get_dir_file_list(cursor.fetchall())

                sql = "SELECT count(0) FROM dir WHERE parent=%d and `delete`=0 UNION SELECT count(0) FROM file WHERE dir=%d and `delete`=0" % (
                    current, current)
                cursor.execute(sql)
                result = cursor.fetchall()
                count = result[0][0]
                if len(result) > 1:
                    count += result[1][0]
        except Exception as err:
            logging.warning(sql)
            raise err
        return results, count

    @mylock
    def update_attribute(self, attr: Attribute):
        ''' update attribute '''
        ok = False

        sql_set = ""
        if attr.encrypt_crc32 is not None:
            sql_set += ", `encrypt_crc32`=%d" % (attr.encrypt_crc32)
        if attr.delete is not None:
            sql_set += ", `delete`=%d" % (attr.delete)
        if attr.check_date is not None:
            sql_set += ", `check_date`=%s" % (safe(attr.check_date))
        sql_set = sql_set.lstrip(',')

        sql = "UPDATE `%s`.attribute SET %s WHERE id=%d" % (
            self.db_name, sql_set, attr.id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = True
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    @mylock
    def update_file(self, file: File):
        ''' update file '''
        ok = False

        sql_set = ""
        if file.attribute is not None:
            sql_set += ", `attribute`=%d" % (file.attribute)
        if file.dir is not None:
            sql_set += ", `dir`=%d" % (file.dir)
        if file.name is not None:
            sql_set += ", `name`=%s" % safe(file.name)
        if file.ext is not None:
            sql_set += ", `ext`=%s" % safe(file.ext)
        if file.delete is not None:
            sql_set += ", `delete`=%d" % (file.delete)
        sql_set = sql_set.lstrip(',')

        sql = "UPDATE `%s`.file SET %s WHERE id=%d" % (
            self.db_name, sql_set, file.id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = True
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    @mylock
    def update_dir(self, dir_model: Dir):
        ''' update dir '''
        ok = False

        sql_set = ""
        if dir_model.parent is not None:
            sql_set += ", `parent`=%d" % (dir_model.parent)
        if dir_model.name is not None:
            sql_set = ", `name`=%s" % safe(dir_model.name)
        if dir_model.delete is not None:
            sql_set += ", `delete`=%d" % (dir_model.delete)
        sql_set = sql_set.lstrip(',')

        sql = "UPDATE `%s`.dir SET %s WHERE id=%d" % (
            self.db_name, sql_set, dir_model.id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = True
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    @mylock
    def update_attribute_tag(self, attribute_tag: AttributeTag):
        ''' update attribute tag '''
        ok = False

        sql_set = ""
        if attribute_tag.tag_id is not None:
            sql_set += ", `tag_id`=%d" % (attribute_tag.tag_id)
        if attribute_tag.target is not None:
            sql_set += ", `target`=%d" % (attribute_tag.target)
        if attribute_tag.type is not None:
            sql_set += ", `type`=%d" % (attribute_tag.type)
        if attribute_tag.delete is not None:
            sql_set += ", `delete`=%d" % (attribute_tag.delete)
        sql_set = sql_set.lstrip(',')

        sql = "UPDATE `%s`.attribute_tag SET %s WHERE id=%d" % (
            self.db_name, sql_set, attribute_tag.id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = True
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    @mylock
    def recover_attribute_tag(self, tag_id: int = None, target: int = None, type_id: int = None):
        ''' recover attribute tag '''
        ok = False

        sql_where = ""
        if tag_id is not None:
            sql_where += " and `tag_id`=%d" % (tag_id)
        if target is not None:
            sql_where += " and `target`=%d" % (target)
        if type_id is not None:
            sql_where += " and `type`=%d" % (type_id)
        sql_where = sql_where.strip().lstrip('and')

        sql = "UPDATE `%s`.attribute_tag SET `delete`=0 WHERE %s" % (
            self.db_name, sql_where)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = cursor.rowcount > 0
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    @mylock
    def update_tag(self, tag: Tag):
        ''' update tag '''
        ok = False

        sql_set = ""
        if tag.key is not None:
            sql_set += ", `key`=%s" % safe(tag.key)
        if tag.value is not None:
            sql_set += ", `value`=%s" % safe(tag.value)
        if tag.delete is not None:
            sql_set += ", `delete`=%d" % (tag.delete)
        sql_set = sql_set.lstrip(',')

        sql = "UPDATE `%s`.tag SET %s WHERE id=%d" % (
            self.db_name, sql_set, tag.id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = True
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    @mylock
    def update_netdisk(self, netdisk: Netdisk):
        ''' update netdisk '''
        ok = False

        sql_set = ""
        if netdisk.access_token is not None:
            sql_set += ", `access_token`=%s" % safe(netdisk.access_token)
        if netdisk.token_expire is not None:
            sql_set += ", `token_expire`='%s'" % (
                netdisk.token_expire.strftime('%Y-%m-%d %H:%M:%S'))
        sql_set = sql_set.lstrip(',')

        sql = "UPDATE `%s`.netdisk SET %s WHERE id=%d" % (
            self.db_name, sql_set, netdisk.id)
        try:
            with self.open_db().cursor() as cursor:
                cursor.execute(sql)
                ok = True
        except Exception as e:
            logging.warning(sql)
            self.rollback()
            raise e
        return ok

    def enum_dirs(self, dir_list, current):
        # enum dirs
        dirs = self.get_dirs(parent=current, delete=0)

        if len(dirs) > 0:
            for obj in dirs:
                dir_list.append(obj.id)
                self.enum_dirs(dir_list, obj.id)
