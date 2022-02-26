''' file '''
import logging
import os
import shutil
import traceback

import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler)
from backend.controller.dir import (get_dir_path)
from backend.model.attribute import Attribute
from backend.model.file import File
from backend.service import workspace
from backend.util import (io)

class Exist(DefaultHandler):
    ''' file exist '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        file_meta = self.request.files["file"][0]

        yield self.exist_executor(wid, file_meta)

    @run_on_executor
    def exist_executor(self, wid, file_meta):
        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        try:
            file_data = file_meta['body']
            file_size = len(file_data)
            file_crc32 = io.get_crc_32(file_data)
            file_sha256 = io.get_sha_256(file_data)

            # if attr exist
            attr_list = space.driver.get_attrs(
                size=file_size, crc32=file_crc32, sha256=file_sha256)
            if len(attr_list) <= 0:
                self.write_json(status="success", data="no_attr")
                return

            # get exist files
            file_model = File()
            file_model.none()
            file_model.attribute = attr_list[0].id
            file_list, _ = space.driver.get_files(file_model)
            if len(file_list) <= 0:
                self.write_json(status="success", data="no_file")
                return

            dup_path = ""
            for current_dir in get_dir_path(space, file_list[0].dir):
                dup_path += current_dir.name + os.path.sep
            dup_path += file_list[0].name + file_list[0].ext
            self.write_json(status="success", data=dup_path)
        except Exception as e:
            logging.info("[file] exception: %s", traceback.format_exc())
            self.write_json(err=e.args[0])
            return

class Upload(DefaultHandler):
    ''' file upload '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        file_meta = self.request.files["file"][0]
        current_id = int(self.get_arg("current"))
        encrypt = self.get_arg("encrypt")

        yield self.upload_executor(wid, file_meta, current_id, encrypt)

    @run_on_executor
    def upload_executor(self, wid, file_meta, current_id, encrypt):
        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # dup image backup dir
        bak_path = os.path.join(space.data_path, "bak")
        os.makedirs(bak_path, exist_ok=True)

        try:
            file_name = file_meta["filename"]
            file_data = file_meta["body"]
            file_size = len(file_data)
            file_crc32 = io.get_crc_32(file_data)
            file_sha256 = io.get_sha_256(file_data)
            file_sp = os.path.splitext(file_name)
            file_ext = file_sp[1].lower() if file_sp[1] is not None else ""

            hash_file_name = io.format_file_name(
                file_size, file_crc32, file_sha256, None)

            # add file
            file_model = File()
            file_model.none()
            file_model.dir = current_id
            file_model.ext = file_ext
            file_model.name = file_sp[0]
            file_id, file_ok = space.driver.add_file(file_model)
            if not file_ok:
                space.driver.rollback()
                self.write_json(status="error", data="add_file")
                return

            # if attr exist
            attr_list = space.driver.get_attrs(
                size=file_size, crc32=file_crc32, sha256=file_sha256)
            if len(attr_list) > 0:
                attr = attr_list[0]
            else:
                # add attr
                attr = Attribute()
                attr.file = file_id
                attr.type = 0
                attr.size = file_size
                attr.crc32 = file_crc32
                attr.sha256 = file_sha256
                attr.ext = file_ext
                attr.encrypt = encrypt
                attr.key = io.random_key(32)
                # add `attribute`
                attr.id, attr_ok = space.driver.add_attribute(attr)
                if not attr_ok:
                    space.driver.rollback()
                    self.write_json(status="error", data="add_attr")
                    return

            # move file
            new_file_path = os.path.abspath(
                os.path.join(space.data_path, hash_file_name))
            if os.path.exists(new_file_path):
                bak_file_path = os.path.join(
                    bak_path, os.path.basename(new_file_path))
                logging.warning(
                    "[upload] dst path exist: %s, copy to: %s", new_file_path, bak_file_path)
                shutil.copy(new_file_path, bak_file_path)
            try:
                if attr.encrypt is not None:
                    io.encrypt_data_to(file_data, attr.key, new_file_path)
                else:
                    with open(new_file_path, 'wb') as f:
                        f.write(file_data)
            except IOError as e:
                space.driver.rollback()
                logging.error("[upload] unable to save file. %s", e)
                self.write_json(status="error", data="save_file")
                return

            # update attribute id to `file`
            file = File()
            file.none()
            file.id = file_id
            file.attribute = attr.id
            update_ok = space.driver.update_file(file)
            if not update_ok:
                space.driver.rollback()
                self.write_json(status="error", data="update_file")
                return

            space.driver.commit()
            self.write_json(status="success", data=file_name)
        except Exception as e:
            logging.info("[file] exception: %s", traceback.format_exc())
            self.write_json(err=e.args[0])
            return
