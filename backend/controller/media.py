''' Media '''
import os
import shutil

from backend.controller.default import DefaultHandler
from backend.service import workspace
from backend.util import io


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

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get attr
        attr_list = space.driver.get_attrs(id=attribute)
        if len(attr_list) <= 0:
            self.write_json(err="no_attr")
            return
        attr = attr_list[0]
        hash_file_name = io.format_file_name(
            attr.size, attr.crc32, attr.sha256, None)
        full_file_name = hash_file_name + attr.ext

        # path
        hash_file_path = os.path.join(space.data_path, hash_file_name)
        if not os.path.exists(hash_file_path):
            self.write_json(err="no_data", data={"file": hash_file_path})
            return
        tmp_path = os.path.join(self.options.static_path, "tmp")
        tmp_file_path = os.path.join(tmp_path, full_file_name)
        tmp_file_name = "tmp/%s" % full_file_name

        # no cache
        if not os.path.exists(tmp_file_path):
            # decrypt
            os.makedirs(tmp_path, exist_ok=True)
            if attr.encrypt is not None and attr.key is not None:
                io.decrypt_file_to(hash_file_path, attr.key, tmp_file_path)
            else:
                shutil.copy(hash_file_path, tmp_file_path)

        # set include_version then browser will use cache
        self.write_json(status="success", data={
                        "src": self.static_url(tmp_file_name, include_version=True)})
