''' Media '''
import os
import shutil

from backend.controller.default import DefaultHandler
from backend.model.tag import Tag
from backend.service import workspace


class Add(DefaultHandler):
    ''' add tag '''

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
        key = self.get_arg("key")
        value = self.get_arg("value")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # add tag
        tag = Tag()
        tag.id = space.driver.get_miss_id("tag")
        tag.target = target
        tag.type = 2 if target_type == "dir" else 1
        tag.key = key
        tag.value = value

        tag.id, ok = space.driver.add_tag(tag)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=tag)


class Update(DefaultHandler):
    ''' update tag '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        id = int(self.get_arg("id"))
        key = self.get_arg("key")
        value = self.get_arg("value")
        delete = self.get_arg("delete")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # delete
        if delete == 1:
            ok = space.driver.delete("tag", id)
            if not ok:
                self.write_json(err="db")
                return
            space.driver.commit()

            self.write_json(status="success")
            return

        # add tag
        tag = Tag()
        tag.id = id
        tag.key = key
        tag.value = value
        tag.delete = delete

        ok = space.driver.update_tag(tag)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=tag)