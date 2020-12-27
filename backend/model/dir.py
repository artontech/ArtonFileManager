''' dir '''
from backend.model.default import DefaultModel

class Dir(DefaultModel):
    id = None
    parent = 0
    name = ""
    delete = 0
    createtime = None
    modtime = None

    # viewer
    icon = ""
    tags = []
    type = "dir"

    def none(self):
        ''' clear '''
        super().none()
        
        self.id = None
        self.parent = None
        self.name = None
        self.delete = None
        self.createtime = None
        self.modtime = None

        # viewer
        self.icon = None
        self.tags = None
        self.type = None

def get_dir_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for i in range(len(db_results)):
        row = db_results[i]
        obj = Dir()
        obj.id = row[0]
        obj.parent = row[1]
        obj.name = row[2]
        obj.delete = row[3]
        obj.createtime = row[4]
        obj.modtime = row[5]
        obj.type = "dir"
        result.append(obj)
    return result