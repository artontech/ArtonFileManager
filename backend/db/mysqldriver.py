import configparser
import datetime
import json
import logging
import os
import signal
import subprocess

import pymysql

from db.driver import Driver
from backend.model.default import DefaultModel
from backend.model.attribute import (
    Attribute,
    get_attribute,
    get_attribute_list
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
from backend.util import io


def safe(s: str, collate: bool = False) -> str:
    ''' escape string for sql '''
    result = "'%s'" % pymysql.escape_string(s)
    if collate:
        result += " COLLATE utf8mb4_general_ci"
    return result


class MySQLDriver(Driver):
    def __init__(self, options, workspace):
        self.database = None
        self.db = None
        self.db_name = r"arton_file_manager"
        self.host = None
        self.json_path = os.path.join(workspace, "afm_config.json")
        self.options = options
        self.password = None
        self.port = None
        self.user = None
        self.workspace = workspace

    def init(self):
        MYSQL_PATH = self.options.mysql_path
        CONFIG_PATH = self.options.config_path
        logging.info("Init mysql at: %s" % (MYSQL_PATH))

        if os.path.exists(self.json_path):
            logging.warning("Workspace already exist: %s" % self.workspace)
            return 0

        os.makedirs(self.workspace, exist_ok=True)

        # add json config
        config_json = {
            "workspace": self.workspace,
            "data_path": os.path.join(self.workspace, "afm_data")
        }
        with open(self.json_path, 'w+') as f:
            json.dump(config_json, f)

        os.makedirs(os.path.join(self.workspace, "mysql/data"))

        # gen config
        ini_src_path = os.path.join(CONFIG_PATH, "mysql.windows.ini")
        ini_dst_path = os.path.join(self.workspace, "mysql.windows.ini")
        with open(ini_src_path, "r") as f:
            ini = f.read()
            ini = ini.replace(r"%port%", "13311")
            ini = ini.replace(
                r"%workspace%", self.workspace.replace("\\", "/"))
            ini = ini.replace(r"%mysql%", os.path.dirname(
                MYSQL_PATH).replace("\\", "/"))
        with open(ini_dst_path, "w+") as f:
            f.write(ini)

        # init service
        cmd = [os.path.join(MYSQL_PATH, "mysqld"),
               "--defaults-file=%s" % (ini_dst_path),
               "--init-file=%s" % os.path.join(CONFIG_PATH,
                                               "mysql.windows.sql"),
               "--initialize"]  # --initialize-insecure
        ret = subprocess.run(cmd)
        return ret.returncode

    def open(self):
        MYSQL_PATH = self.options.mysql_path
        ini_path = os.path.join(self.workspace, "mysql.windows.ini")
        logging.info("Open mysql at: %s" % (MYSQL_PATH))

        # load config
        if not os.path.exists(self.json_path):
            logging.warning("No json config: %s" % self.workspace)
            return -1
        with open(self.json_path, 'r+') as f:
            config_json = json.load(f)
        last_workspace = config_json.get("workspace", self.workspace)
        self.host = config_json.get("host", "localhost")
        self.user = config_json.get("user", "root")
        self.password = config_json.get("password", "")
        self.database = config_json.get("database", "arton_file_manager")
        self.port = config_json.get("port", 13311)

        # if workspace changed, fix mysql
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
            config_json["workspace"] = self.workspace
            with open(self.json_path, 'w+') as f:
                json.dump(config_json, f)

        cmd = [os.path.join(MYSQL_PATH, "mysqld"),
               "--install", "ArtonFileManagerMySQL",
               "--defaults-file=%s" % (ini_path)]
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            return ret

        cmd = ["net", "start", "ArtonFileManagerMySQL"]
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            return ret

        if self.open_db() is None:
            ret.returncode = -99
            return ret

        return ret

    def close(self):
        self.close_db()

        result = True

        cmd = ["net", "stop", "ArtonFileManagerMySQL"]
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            result = False

        cmd = ["sc", "delete", "ArtonFileManagerMySQL"]
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            result = False

        return result

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

    def get_dir_file_list(self, db_results):
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
                self.commit()
        except Exception as err:
            logging.warning(sql)
            raise err

        return result

    def get_miss_ids(self, table: str, limit: int = None) -> list:
        ''' get id gap '''

        result = []
        # reset auto_increment if table is empty
        if self.get_a_row(table) is None:
            self.reset_auto_increment(table)
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

    def delete(self, table: str, id: str) -> bool:
        ''' delete by id '''

        ok = False
        sql = "DELETE FROM `%s` WHERE `id`=%s" % (table, id)
        try:
            with self.open_db().cursor() as cursor:
                r = cursor.execute(sql)
                ok = r > 0
        except Exception as err:
            logging.warning(sql)
            raise err

        return ok

    def add_file(self, file: File) -> bool:
        ''' add file '''
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ok = True

        if file.id is None:
            id = "NULL"
        else:
            id = "'%s'" % file.id
        if file.name is None:
            name = "NULL"
        else:
            name = "%s" % safe(file.name)
        if file.ext is None:
            ext = "NULL"
        else:
            ext = "%s" % safe(file.ext)

        sql = "INSERT INTO `%s`.file (`id`,`dir`,`attribute`,`name`,`ext`,`delete`,`createtime`,`modtime`) \
            VALUES (%s,%s,NULL,%s,%s,0,'%s','%s');" % (self.db_name, id, file.dir, name, ext, time_now, time_now)
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

    def add_dir(self, dir_model: Dir):
        ''' add new dir to database '''
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_id = 0
        ok = False

        if dir_model.id is None:
            id = "NULL"
        else:
            id = "'%s'" % dir_model.id
        if dir_model.parent is None:
            parent = 0
        else:
            parent = "%d" % dir_model.parent
        if dir_model.name is None:
            name = "NULL"
        else:
            name = "%s" % safe(dir_model.name)

        sql = "INSERT INTO `%s`.dir (`id`,`parent`,`name`,`delete`,`createtime`,`modtime`) VALUES \
            (%s,%s,%s,0,'%s','%s');" % (self.db_name, id, parent, name, time_now, time_now)
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

    def add_attribute(self, attr: Attribute):
        ''' add new attr to database '''
        current_id = "NULL"
        ok = False

        if attr.id is None:
            id = "NULL"
        else:
            id = "'%s'" % attr.id
        if attr.encrypt is None:
            encrypt = "NULL"
        else:
            encrypt = "'%s'" % attr.encrypt
        if attr.key is None:
            key = "NULL"
        else:
            key = "'%s'" % attr.key

        sql = "INSERT INTO `%s`.attribute (`id`,`file`,`type`,`size`,`crc32`,`sha256`,`ext`,`width`,`height`,`color`, \
            `ahash`,`phash`,`dhash`,`desc`,`encrypt`,`key`) VALUES (%s,%s,%d,%d,'%s','%s',%s,%d,%d,'%s',%d,%d,%d, \
            %s,%s,%s);" % (self.db_name, id, attr.file, attr.type, attr.size, attr.crc32, attr.sha256, safe(attr.ext),
                           attr.width, attr.height, attr.color, attr.ahash, attr.phash, attr.dhash, safe(
                               attr.desc),
                           encrypt, key)
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

    def add_attribute_tag(self, attribute_tag: AttributeTag):
        ''' add new attribute tag to database '''
        current_id = "NULL"
        ok = False

        if attribute_tag.id is None:
            id = "NULL"
        else:
            id = "'%s'" % attribute_tag.id

        sql = "INSERT INTO `%s`.attribute_tag (`id`,`tag_id`,`target`,`type`,`delete`) VALUES (%s,%d,%d,%d,0);" % (
            self.db_name, id, attribute_tag.tag_id, attribute_tag.target, attribute_tag.type)
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

    def add_tag(self, tag: Tag):
        ''' add new tag to database '''
        current_id = "NULL"
        ok = False

        if tag.id is None:
            id = "NULL"
        else:
            id = "'%s'" % tag.id

        sql = "INSERT INTO `%s`.tag (`id`,`key`,`value`,`delete`) VALUES (%s,%s,%s,0);" % (
            self.db_name, id, safe(tag.key), safe(tag.value))
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

    def get_dirs(self, id=None, parent: int = None, delete: int = None, name: str = None):
        ''' list dirs '''
        results = []

        sql_where = ""
        if id is not None:
            sql_where += " and `id`=%s" % (id)
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

    def get_attrs(self, id=None, size: int = None, crc32: int = None, sha256: str = None):
        ''' list files '''
        results = []

        sql_where = ""
        if id is not None:
            sql_where += " and `id`=%s" % (id)
        if size is not None:
            sql_where += " and `size`=%d" % (size)
        if crc32 is not None:
            sql_where += " and `crc32`=%d" % (crc32)
        if sha256 is not None:
            sql_where += " and `sha256`='%s'" % (sha256)
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

    def get_attribute_tags(self, id=None, tag_id: int = None, target: int = None, type_id: int = None, delete: int = 0):
        ''' list attribute tags '''
        results = []

        sql_where = ""
        if id is not None:
            sql_where += " and `id`=%s" % (id)
        if tag_id is not None:
            sql_where += " and `tag_id`=%d" % (tag_id)
        if target is not None:
            sql_where += " and `target`=%d" % (target)
        if type_id is not None:
            sql_where += " and `type`=%d" % (type_id)
        if delete is not None:
            sql_where += " and `delete`='%s'" % (delete)
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

    def get_tags(self, id=None, key: str = None, value: str = None, delete: int = 0):
        ''' list tags '''
        results = []

        sql_where = ""
        if id is not None:
            sql_where += " and `id`=%s" % (id)
        if key is not None:
            sql_where += " and `key`=%s" % safe(key)
        if value is not None:
            sql_where += " and `value`=%s" % safe(value)
        if delete is not None:
            sql_where += " and `delete`='%s'" % (delete)
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

    def union_attribute_tags(self, id=None, target: int = None, type_id: int = None, delete: int = 0):
        ''' list union attribute tags '''
        results = []

        sql_where = ""
        if id is not None:
            sql_where += " and `at`.`id`=%s" % (id)
        if target is not None:
            sql_where += " and `at`.`target`=%d" % (target)
        if type_id is not None:
            sql_where += " and `at`.`type`=%d" % (type_id)
        if delete is not None:
            sql_where += " and `at`.`delete`='%s'" % (delete)
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

                sql = "SELECT count(0) FROM dir WHERE parent=%d UNION SELECT count(0) FROM file WHERE dir=%d" % (
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

    def update_file(self, file: File):
        ''' update file '''
        ok = False

        sql_set = ""
        if file.attribute is not None:
            sql_set += ", `attribute`=%d" % (file.attribute)
        if file.dir is not None:
            sql_set += ", `dir`=%d" % (file.dir)
        if file.name is not None:
            sql_set = ", `name`=%s" % safe(file.name)
        if file.ext is not None:
            ext = ", `ext`=%s" % safe(file.ext)
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

    def enum_dirs(self, dir_list, current):
        # enum dirs
        dirs = self.get_dirs(parent=current, delete=0)

        if len(dirs) > 0:
            for obj in dirs:
                dir_list.append(obj.id)
                self.enum_dirs(dir_list, obj.id)
