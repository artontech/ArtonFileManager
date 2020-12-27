''' file '''
from backend.model.default import DefaultModel

class File(DefaultModel):
    id = None
    dir = 0
    attribute = 0
    name = ""
    ext = ""
    delete = 0
    createtime = None
    modtime = None

    # viewer
    icon = ""
    thumb = ""
    attr = None
    tags = []
    type = "file"

    def none(self):
        ''' clear '''
        super().none()

        self.id = None
        self.dir = None
        self.attribute = None
        self.name = None
        self.ext = None
        self.delete = None
        self.createtime = None
        self.modtime = None

        # viewer
        self.icon = None
        self.thumb = None
        self.attr = None
        self.tags = None
        self.type = None

def get_file_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for i in range(len(db_results)):
        row = db_results[i]
        obj = File()
        obj.id = row[0]
        obj.dir = row[1]
        obj.attribute = row[2]
        obj.name = row[3]
        obj.ext = row[4]
        obj.delete = row[5]
        obj.createtime = row[6]
        obj.modtime = row[7]
        obj.type = "file"
        result.append(obj)
    return result