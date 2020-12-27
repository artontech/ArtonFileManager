''' Attribute tag '''
from backend.controller.default import DefaultHandler
from backend.model.attributetag import AttributeTag
from backend.service import workspace


USE_LOGIC_DELETE = True


class Add(DefaultHandler):
    ''' add attribute tag '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        tag_id = int(self.get_arg("tag_id"))
        target = int(self.get_arg("target"))
        target_type = self.get_arg("type")
        type_id = 2 if target_type == "dir" else 1

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # recover deleted attribute tag
        ok = space.driver.recover_attribute_tag(tag_id, target, type_id)
        if ok:
            attribute_tags = space.driver.get_attribute_tags(tag_id=tag_id, target=target, type_id=type_id)
            space.driver.commit()
            self.write_json(status="success", data=attribute_tags[0])
            return

        # new attribute tag
        attribute_tag = AttributeTag()
        attribute_tag.id = space.driver.get_miss_id("attribute_tag")
        attribute_tag.tag_id = tag_id
        attribute_tag.target = target
        attribute_tag.type = type_id

        attribute_tag.id, ok = space.driver.add_attribute_tag(attribute_tag)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=attribute_tag)


class Update(DefaultHandler):
    ''' update attribute tag '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        id = int(self.get_arg("id"))
        delete = self.get_arg("delete")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # delete
        if not USE_LOGIC_DELETE and delete == 1:
            ok = space.driver.delete("attribute_tag", id)
            if not ok:
                self.write_json(err="db")
                return
            space.driver.commit()

            self.write_json(status="success")
            return

        # add attribute tag
        attribute_tag = AttributeTag()
        attribute_tag.id = id
        attribute_tag.delete = delete

        ok = space.driver.update_attribute_tag(attribute_tag)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=attribute_tag)
