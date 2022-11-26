''' Media '''
import logging
import os
import shutil

from backend.controller.default import DefaultHandler
from backend.service import workspace
from backend.util import (ffmpeg, fileio, url)


class Link(DefaultHandler):
    ''' get file link '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        attribute = self.get_arg("attribute")
        filename = self.get_arg("filename")
        cache = self.get_arg("cache", "").lower() == "true"

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get attr
        attr_list = space.driver.get_attrs(item_id=attribute)
        if len(attr_list) <= 0:
            self.write_json(err="no_attr")
            return
        attr = attr_list[0]
        hash_file_name = fileio.format_file_name(
            attr.size, attr.crc32, attr.sha256, None)
        full_file_name = hash_file_name + attr.ext

        # path
        hash_file_path = os.path.join(space.data_path, hash_file_name)
        if not os.path.exists(hash_file_path):
            self.write_json(err="no_data", data={"file": hash_file_path}, status_code=404)
            return

        if cache:
            tmp_file_path = os.path.join(self.options.tmp_path, full_file_name)

            # no cache
            if not os.path.exists(tmp_file_path):
                # decrypt
                os.makedirs(self.options.tmp_path, exist_ok=True)
                if attr.encrypt is not None and attr.key is not None:
                    fileio.decrypt_file_to(hash_file_path, attr.key, tmp_file_path)
                else:
                    shutil.copy(hash_file_path, tmp_file_path)

            # set include_version then browser will use cache
            # self.write_json(status="success", data={
            #                 "src": self.static_url(tmp_file_name, include_version=True)})

            with open(tmp_file_path, 'rb') as f:
                data = f.read()
        else:
            if attr.encrypt is not None and attr.key is not None:
                data, _, _ = fileio.decrypt_file_stream(hash_file_path, attr.key)
            else:
                with open(hash_file_path, 'rb') as f:
                    data = f.read()

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', f'attachment; filename="{url.encode(filename)}"')
        self.write(data)


class VideoThumb(DefaultHandler):
    ''' get video thumb link '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        def finish(data):
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', f'attachment; filename="{url.encode(filename)}"')
            self.write(data)

        wid = self.get_arg("wid")
        attribute = self.get_arg("attribute")
        filename = self.get_arg("filename")
        limit = int(self.get_arg("limit", default=10))
        thumbtype = self.get_arg("thumbtype", default="gif")
        cache = self.get_arg("cache", "").lower() == "true"

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get attr
        attr_list = space.driver.get_attrs(item_id=attribute)
        if len(attr_list) <= 0:
            self.write_json(err="no_attr")
            return
        attr = attr_list[0]
        hash_file_name = fileio.format_file_name(attr.size, attr.crc32, attr.sha256, None)

        # has thumb cache
        tmp_thumb_path = os.path.join(self.options.tmp_path, hash_file_name + f"_thumb.{thumbtype}")
        if os.path.exists(tmp_thumb_path):
            finish(fileio.read_bin(tmp_thumb_path))
            return

        # check src file exist
        hash_file_path = os.path.join(space.data_path, hash_file_name)
        if not os.path.exists(hash_file_path):
            self.write_json(err="no_data", data={"file": hash_file_path}, status_code=404)
            return
        os.makedirs(self.options.tmp_path, exist_ok=True)

        # decrypt
        if attr.encrypt is not None and attr.key is not None:
            video_data, _, _ = fileio.decrypt_file_stream(hash_file_path, attr.key, chunk_limit=limit)
        else:
            video_data = fileio.read_bin(hash_file_path)

        # gen thumb
        thumb_data, err = ffmpeg.stream2thumb(video_data, thumb_type=thumbtype)
        if err:
            logging.error("[media] ffmpeg: path=%s wid=%s", hash_file_path, str(err, encoding="utf-8"))
        if cache:
            fileio.write_bin(tmp_thumb_path, thumb_data)

        finish(thumb_data)

class Export(DefaultHandler):
    ''' export media '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        targets = self.get_arg("targets")
        export_path = os.path.abspath(self.get_arg("export_path"))

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # process
        for target in targets:
            if target["type"] != "file":
                continue

            # get attr
            attr_list = space.driver.get_attrs(item_id=target["attribute"])
            if len(attr_list) <= 0:
                self.write_json(err="no_attr")
                return
            attr = attr_list[0]
            hash_file_name = fileio.format_file_name(
                attr.size, attr.crc32, attr.sha256, None)

            # export
            file_path = os.path.join(export_path, hash_file_name + target["ext"])
            if os.path.exists(file_path):
                continue

            # path
            hash_file_path = os.path.join(space.data_path, hash_file_name)
            if not os.path.exists(hash_file_path):
                self.write_json(err="no_data", data={
                    "file": hash_file_path})
                return

            # decrypt
            if attr.encrypt is not None and attr.key is not None:
                fileio.decrypt_file_to(hash_file_path, attr.key, file_path)
            else:
                shutil.copy(hash_file_path, file_path)

        self.write_json(status="success", data=export_path)
