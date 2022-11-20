''' dir '''

import json
import logging
import os
import shutil
import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.model.attribute import Attribute
from backend.model.dir import Dir
from backend.model.file import File
from backend.service import workspace
from backend.util import (fileio, image, string)


def get_dir_path(space, dir_id: int):
    ''' get full dir path '''
    current = dir_id
    dir_path = []
    for _ in range(100):
        dir_list = space.driver.get_dirs(item_id=current)
        if len(dir_list) <= 0:
            break
        dir_path.insert(0, dir_list[0])
        current = dir_list[0].parent
        if not current:
            break
    return dir_path

class DirWebSocket(DefaultWSHandler):
    name = "dir"

    def open(self):
        logging.info("[ws] Dir WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            wid = msg_json.get("wid", None)
            logging.info("[ws] dir init: wid=%s", wid)
            if wid is None:
                self.write_json(msg_type="init", err="no_wid")
                return

            self.space = workspace.get_by_id(wid)
            if self.space is None or not self.space.enabled:
                self.write_json(msg_type="init", err="no_workspace")
                return
            self.space.add_ws(self)
            self.write_json(msg_type="init", status="success",
                            data=self.space.serializable())

    def on_close(self):
        logging.info("[ws] close")
        if hasattr(self, "space") and self.space is not None:
            self.space.del_ws(self)


class Import(DefaultHandler):
    ''' import dir '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        path = self.get_arg("path")
        base_id = int(self.get_arg("current"))
        delete = self.get_arg("delete")
        encrypt = self.get_arg("encrypt")

        yield self.import_dir(wid, path, base_id, delete, encrypt)

    @run_on_executor
    def import_dir(self, wid, path, base_id, delete, encrypt):
        # trim input
        if not isinstance(encrypt, str) or encrypt.strip() == "":
            encrypt = None

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # dup image backup dir
        bak_path = os.path.join(space.data_path, "bak")
        os.makedirs(bak_path, exist_ok=True)

        # prepare miss id
        miss_attribute_id = space.driver.get_miss_ids("attribute")
        miss_dir_id = space.driver.get_miss_ids("dir")
        miss_file_id = space.driver.get_miss_ids("file")

        # get directory structure, write to database table `dir` & `file`
        dir_id_map = {}
        id_dir_map = {}
        dir_len = 0
        for current, _, files in os.walk(path):
            if current not in dir_id_map:
                dir_name = os.path.basename(current)
                parent = os.path.dirname(current)
                parent_id = dir_id_map.get(parent, {}).get("id", base_id)

                # check exist
                dir_list = space.driver.get_dirs(
                    parent=parent_id, delete=0, name=dir_name)
                if len(dir_list) > 0:
                    current_id = dir_list[0].id
                    dir_ok = True
                    logging.info("existing dir %s:%s", current_id, current)
                else:
                    # add dir to table `dir`
                    dir_model = Dir()
                    # if has miss id, use it
                    if len(miss_dir_id) > 0:
                        dir_model.id = miss_dir_id[0]
                    dir_model.parent = parent_id
                    dir_model.name = dir_name
                    current_id, dir_ok = space.driver.add_dir(dir_model)
                    logging.info("add dir %s:%s", current_id, current)
                    # remove id
                    if dir_ok and current_id in miss_dir_id:
                        miss_dir_id.remove(current_id)
                dir_id_map[current] = {"id": current_id, "parent": parent_id}
                id_dir_map[current_id] = current

                # add files to table `file`
                file_ok = True
                if len(files) > 0:
                    # gen exist file dict
                    file_model = File()
                    file_model.none()
                    file_model.dir = current_id
                    file_model.delete = 0
                    file_list, _ = space.driver.get_files(file_model)
                    exist_files = {}
                    for obj in file_list:
                        f = obj.name + obj.ext
                        exist_files[f] = True

                    # add files
                    for f in files:
                        if not exist_files.get(f, False):
                            sp = os.path.splitext(f)
                            ext = sp[1].lower() if sp[1] is not None else ""
                            file = File()
                            # if has missing id, use it
                            if len(miss_file_id) > 0:
                                file.id = miss_file_id[0]
                            file.dir = current_id
                            file.name = sp[0]
                            file.ext = ext
                            file_id, file_ok = space.driver.add_file(file)
                            if not file_ok:
                                break
                            if file_id in miss_file_id:
                                miss_file_id.remove(file_id)
                if dir_ok and file_ok:
                    space.driver.commit()
                else:
                    space.driver.rollback()
                    space.send_ws(name="dir", msg_type="import", err="db", data={
                        "type": "msg", "msg": "structure_fail"
                    })
                    self.write_json(err="structure_fail")
                    return
            dir_len += 1
            if dir_len % 100 == 0:
                space.send_ws(name="dir", msg_type="import", status="run", data={
                    "type": "dir", "now": dir_len
                })

        space.send_ws(name="dir", msg_type="import", status="run", data={
            "type": "msg", "msg": "structure_done"
        })

        # get file list (not processed)
        file_model = File()
        file_model.none()
        file_model.delete = 0
        file_list, _ = space.driver.get_files(file_model, attr_null=True)
        file_list_len = len(file_list)
        step = int(file_list_len / 100) + 1
        for i in range(file_list_len):
            file_id = file_list[i].id
            dir_id = file_list[i].dir
            file_ext = file_list[i].ext
            file_name = file_list[i].name
            file_path = os.path.join(id_dir_map.get(
                dir_id, None), string.join(file_name, file_ext))
            logging.info("Now: %d, %s", file_id, file_path)

            # open file & find dup CRC & SHA
            with open(file_path, "rb") as f:
                file_data = f.read()
            file_size = fileio.get_file_size(file_path)
            file_crc32 = fileio.get_crc_32(file_data)
            file_sha256 = fileio.get_sha_256(file_data)

            # if attr exist
            hash_file_name = fileio.format_file_name(
                file_size, file_crc32, file_sha256, None)
            move_file_ok = True
            attr_list = space.driver.get_attrs(
                size=file_size, crc32=file_crc32, sha256=file_sha256)
            attr = None
            if len(attr_list) > 0:
                attr = attr_list[0]
                logging.warning("[import] duplicate file %s with %s(%s)",
                                file_path, attr.file, attr.id)
                space.send_ws(name="dir", msg_type="import", status="run", data={
                    "type": "warn", "msg": "dup_file", "file": file_path, "files": [attr.file, file_id]
                })
                attr_ok = True
            else:
                # add attr
                attr = Attribute()
                # if has miss id, use it
                if len(miss_attribute_id) > 0:
                    attr.id = miss_attribute_id[0]
                attr.file = file_id
                attr.type = 0
                attr.size = file_size
                attr.crc32 = file_crc32
                attr.sha256 = file_sha256
                attr.ext = file_ext
                attr.encrypt = encrypt
                attr.key = fileio.random_key(32)

                # load image info
                if fileio.is_cv_support(attr.ext):
                    try:
                        img = image.parse_image(file_data)
                        attr.height = img.shape[0]
                        attr.width = img.shape[1]
                    except Exception as e:
                        logging.error(
                            "[import] unable to load image %s. %s", file_path, e)
                        space.send_ws(name="dir", msg_type="import", status="run", data={
                            "type": "warn", "msg": "load_img_fail", "file": file_path})
                    try:
                        attr.ahash = image.a_hash(img)
                        attr.dhash = image.d_hash(img)
                        attr.phash = image.p_hash(img)
                    except Exception as e:
                        logging.error(
                            "[import] unable to calc image hash %s. %s", file_path, e)
                        space.send_ws(name="dir", msg_type="import", status="run", data={
                            "type": "warn", "msg": "calc_hash_fail", "file": file_path})

                # move file
                new_file_path = os.path.abspath(
                    os.path.join(space.data_path, hash_file_name))
                if os.path.exists(new_file_path):
                    bak_file_path = os.path.join(
                        bak_path, os.path.basename(new_file_path))
                    logging.warning(
                        "[import] dst path exist: %s, copy to: %s", new_file_path, bak_file_path)
                    shutil.copy(new_file_path, bak_file_path)
                try:
                    if attr.encrypt is not None:
                        fileio.encrypt_data_to(
                            file_data, attr.key, new_file_path)
                        if delete:
                            os.remove(file_path)
                    else:
                        if delete:
                            os.rename(file_path, new_file_path)
                        else:
                            shutil.copy(file_path, new_file_path)
                except IOError as e:
                    move_file_ok = False
                    logging.error("[import] unable to copy file. %s", e)
                    space.send_ws(name="dir", msg_type="import", data={
                        "type": "msg", "msg": "io_error", "file": file_path, "error": e.strerror})

                # add `attribute`
                attr.id, attr_ok = space.driver.add_attribute(attr)
                # remove id
                if attr_ok and attr.id in miss_attribute_id:
                    miss_attribute_id.remove(attr.id)

            # update attribute id and hash file name to `file`
            file = File()
            file.none()
            file.id = file_id
            file.attribute = attr.id
            update_ok = space.driver.update_file(file)
            if attr_ok and update_ok and move_file_ok:
                space.driver.commit()
            else:
                space.driver.rollback()
                space.send_ws(name="dir", msg_type="import", data={
                    "type": "msg", "msg": "attr_fail"})
                self.write_json(err="attr_fail")
                return

            if i % step == 0:
                space.send_ws(name="dir", msg_type="import", status="run", data={
                    "type": "files_progress", "total": file_list_len, "now": i})

        space.send_ws(name="dir", msg_type="import", status="success", data={
            "type": "msg", "msg": "import_done"
        })
        self.write_json(status="success", data=file_list_len)


class Export(DefaultHandler):
    ''' export dir '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        current = self.get_arg("current")
        name = self.get_arg("name")
        path = os.path.abspath(self.get_arg("path"))

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # process
        id_dir_map = {
            current: os.path.join(path, name)
        }
        dir_stack = [current]
        while len(dir_stack) > 0:
            dir_id = dir_stack.pop()
            dir_path = id_dir_map.get(dir_id, None)
            if dir_path is None:
                logging.warning("[export] dir_path is none %s", dir_id)
                continue
            os.makedirs(dir_path, exist_ok=True)

            # fetch from db
            result_list, _ = space.driver.get_dirs_files(current=dir_id)
            for obj in result_list:
                if obj.type == "dir":
                    if id_dir_map.get(obj.id, None) is not None:
                        continue
                    id_dir_map[obj.id] = os.path.join(dir_path, obj.name)
                    dir_stack.append(obj.id)
                elif obj.type == "file":
                    # export
                    file_path = os.path.join(dir_path, obj.name + obj.ext)
                    if os.path.exists(file_path):
                        continue

                    # get attr
                    attr_list = space.driver.get_attrs(item_id=obj.attribute)
                    if len(attr_list) <= 0:
                        self.write_json(err="no_attr")
                        return
                    attr = attr_list[0]
                    hash_file_name = fileio.format_file_name(
                        attr.size, attr.crc32, attr.sha256, None)

                    # path
                    hash_file_path = os.path.join(
                        space.data_path, hash_file_name)
                    if not os.path.exists(hash_file_path):
                        self.write_json(err="no_data", data={
                            "file": hash_file_path})
                        return

                    # decrypt
                    if attr.encrypt is not None and attr.key is not None:
                        fileio.decrypt_file_to(hash_file_path, attr.key, file_path)
                    else:
                        shutil.copy(hash_file_path, file_path)

        self.write_json(status="success", data=current)


class List(DefaultHandler):
    ''' list dir '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        current = int(self.get_arg("current"))
        show_thumb = string.str2bool(self.get_arg("thumb"))
        get_dir = string.str2bool(self.get_arg("dir"))
        get_file = string.str2bool(self.get_arg("file"))
        page_no = self.get_arg("page_no", default=None)
        page_size = self.get_arg("page_size", default=None)

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # fetch from db
        result_list = []
        total = None
        if get_dir and get_file:
            result_list, total = space.driver.get_dirs_files(
                current, page_no, page_size)
        elif get_dir:
            dir_list = space.driver.get_dirs(parent=current, delete=0)
            result_list.extend(dir_list)
        elif get_file:
            file_model = File()
            file_model.none()
            file_model.dir = current
            file_model.delete = 0
            file_list, _ = space.driver.get_files(file_model)
            result_list.extend(file_list)

        # process
        for obj in result_list:
            if obj.type == "dir":
                obj.icon = self.static_url("folder.png", include_version=False)

                # get attribute tag
                obj.tags = space.driver.union_attribute_tags(
                    target=obj.id, type_id=2)
            elif obj.type == "file":
                obj.icon = self.static_url(fileio.get_icon_name(
                    obj.ext) + ".png", include_version=False)
                if show_thumb and fileio.is_web_img(obj.ext):
                    obj.thumb = "/media/link?wid=%s&attribute=%s" % (
                        wid, obj.attribute)

                # get attr
                attr_list = space.driver.get_attrs(item_id=obj.attribute)
                if len(attr_list) <= 0:
                    self.write_json(err="no_attr")
                    return
                obj.attr = attr_list[0]

                # get attribute tag by attribute id
                obj.tags = space.driver.union_attribute_tags(
                    target=obj.attribute, type_id=1)

        self.write_json(status="success", data={
                        "list": result_list, "total": total})


class Detail(DefaultHandler):
    ''' file or dir detail '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        target = int(self.get_arg("target"))
        target_type = self.get_arg("type")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        if target_type == "file":
            # get attr
            attr_list = space.driver.get_attrs(item_id=target)
            if len(attr_list) <= 0:
                self.write_json(err="no_attr")
                return
            attr = attr_list[0]

            self.write_json(status="success", data=attr)
            return
        elif target_type == "dir":
            result = {}
            size = 0
            file_count = 0

            # get dirs
            dir_list = [target]
            space.driver.enum_dirs(dir_list, target)

            # enum files
            file_model = File()
            for dir_id in dir_list:
                file_model.none()
                file_model.dir = dir_id
                file_model.delete = 0
                file_list, _ = space.driver.get_files(file_model)
                if len(file_list) <= 0:
                    continue

                file_count += len(file_list)
                for obj in file_list:
                    # get attr
                    attr_list = space.driver.get_attrs(item_id=obj.attribute)
                    if len(attr_list) <= 0:
                        self.write_json(err="no_attr")
                        return
                    attr = attr_list[0]
                    size += attr.size

            result["dir_count"] = len(dir_list) - 1
            result["file_count"] = file_count
            result["size"] = size
            self.write_json(status="success", data=result)
            return

        self.write_json(err="unknown_type")


class Create(DefaultHandler):
    ''' create dir '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        current = self.get_arg("current")
        dir_name = self.get_arg("name")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # check exist
        dir_list = space.driver.get_dirs(
            parent=current, delete=0, name=dir_name)
        if len(dir_list) > 0:
            current_id = dir_list[0].id
            logging.info("existing dir %s:%s", current_id, current)
            self.write_json(err="dir_exist")
            return
        else:
            # add dir to table `dir`
            dir_model = Dir()
            dir_model.parent = current
            dir_model.name = dir_name
            current_id, dir_ok = space.driver.add_dir(dir_model)
            logging.info("add dir %s:%s", current_id, current)

            # commit to db
            if dir_ok:
                space.driver.commit()
            else:
                space.driver.rollback()
                self.write_json(err="db")
                return

            self.write_json(status="success", data=current_id)


class MoveTo(DefaultHandler):
    ''' move to dir '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        target_type = self.get_arg("type")
        id_from = self.get_arg("from")
        id_to = self.get_arg("to")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        update_ok = False
        if target_type == "file":
            # update dir id of file
            file = File()
            file.none()
            file.id = id_from
            file.dir = id_to
            update_ok = space.driver.update_file(file)
        elif target_type == "dir":
            # update parent of dir
            dir_model = Dir()
            dir_model.none()
            dir_model.id = id_from
            dir_model.parent = id_to
            update_ok = space.driver.update_dir(dir_model)
        else:
            self.write_json(err="unknown_type")
            return

        # commit to db
        if update_ok:
            space.driver.commit()
        else:
            space.driver.rollback()
            self.write_json(err="db")
            return

        self.write_json(status="success", data=id_to)


class Update(DefaultHandler):
    ''' update '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        types = str(self.get_arg("type")).split(',')
        targets = [int(s) for s in str(self.get_arg("target")).split(',')]
        name = self.get_arg("name", default=None)
        ext = self.get_arg("ext", default=None)
        delete = self.get_arg("delete", default=None)

        # check param
        total = len(types)
        if total != len(targets):
            self.write_json(err="param")
            return

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        update_ok = False
        for i in range(total):
            target_type = types[i]
            target = targets[i]
            if target_type == "file":
                # update dir id of file
                file = File()
                file.none()
                file.id = target
                file.name = name
                file.ext = ext
                file.delete = delete
                update_ok = space.driver.update_file(file)
            elif target_type == "dir":
                # update parent of dir
                dir_model = Dir()
                dir_model.none()
                dir_model.id = target
                dir_model.name = name
                dir_model.delete = delete
                update_ok = space.driver.update_dir(dir_model)
            else:
                self.write_json(err="unknown_type")
                return

            if not update_ok:
                break

        # commit to db
        if update_ok:
            space.driver.commit()
        else:
            space.driver.rollback()
            self.write_json(err="db")
            return

        self.write_json(status="success", data=len(targets))
