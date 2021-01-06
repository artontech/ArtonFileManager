''' router '''
from tornado.web import Application

from backend.controller import dir as cdir, workspace, error, media, tag, attributetag
from backend import config

def make_app():
    ''' make app '''
    options = config.get_options()
    return Application([
        (r"/dir", cdir.DirWebSocket),
        (r"/dir/import", cdir.Import, dict(name="import")),
        (r"/dir/export", cdir.Export, dict(name="export")),
        (r"/dir/list", cdir.List, dict(name="list")),
        (r"/dir/detail", cdir.Detail, dict(name="detail")),
        (r"/dir/create", cdir.Create, dict(name="create")),
        (r"/dir/moveto", cdir.MoveTo, dict(name="move to")),
        (r"/dir/update", cdir.Update, dict(name="update")),

        (r"/workspace/ping", workspace.Ping, dict(name="ping")),
        (r"/workspace/init", workspace.Init, dict(name="init")),
        (r"/workspace/open", workspace.Open, dict(name="open")),
        (r"/workspace/close", workspace.Close, dict(name="close")),

        (r"/media/link", media.Link, dict(name="get file link")),

        (r"/tag/add", tag.Add, dict(name="add tag")),
        (r"/tag/list", tag.List, dict(name="list tag")),
        (r"/tag/update", tag.Update, dict(name="update tag")),

        (r"/attributetag/add", attributetag.Add, dict(name="add attribute tag")),
        (r"/attributetag/update", attributetag.Update, dict(name="update attribute tag")),

        (r"/", error.NotFound)
    ], **options.settings)