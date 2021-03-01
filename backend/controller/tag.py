''' Attribute tag '''

from backend.controller.default import DefaultHandler
from backend.model.tag import Tag
from backend.service import workspace


USE_LOGIC_DELETE = True


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
        tag.key = key
        tag.value = value

        tag.id, ok = space.driver.add_tag(tag)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=tag)


class List(DefaultHandler):
    ''' list tag '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get tags
        tags = space.driver.get_tags(delete=0)
        if tags is None:
            self.write_json(err="db")
            return

        self.write_json(status="success", data=tags)


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
        item_id = int(self.get_arg("id"))
        delete = self.get_arg("delete")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # delete
        if not USE_LOGIC_DELETE and delete == 1:
            ok = space.driver.delete("tag", item_id)
            if not ok:
                self.write_json(err="db")
                return
            space.driver.commit()

            self.write_json(status="success")
            return

        # add tag
        tag = Tag()
        tag.id = id
        tag.delete = delete

        ok = space.driver.update_tag(tag)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=tag)
