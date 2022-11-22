''' router '''
from tornado.web import Application

from backend.controller import (
    attributetag,
    backup,
    baidunetdisk,
    check,
    dir as cdir,
    error,
    file as cfile,
    media,
    oss,
    tag,
    searchfile,
    workspace
)
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
        (r"/dir/getdir", cdir.GetDir, dict(name="get dir")),

        (r"/file/exist", cfile.Exist, dict(name="exist")),
        (r"/file/upload", cfile.Upload, dict(name="upload")),

        (r"/workspace/ping", workspace.Ping, dict(name="ping")),
        (r"/workspace/init", workspace.Init, dict(name="init")),
        (r"/workspace/open", workspace.Open, dict(name="open")),
        (r"/workspace/close", workspace.Close, dict(name="close")),

        (r"/media/link", media.Link, dict(name="get file link")),
        (r"/media/export", media.Export, dict(name="export media")),

        (r"/tag/add", tag.Add, dict(name="add tag")),
        (r"/tag/list", tag.List, dict(name="list tag")),
        (r"/tag/update", tag.Update, dict(name="update tag")),

        (r"/attributetag/add", attributetag.Add, dict(name="add attribute tag")),
        (r"/attributetag/update", attributetag.Update, dict(name="update attribute tag")),

        (r"/baidunetdisk", baidunetdisk.BaiduWebSocket),
        (r"/baidunetdisk/oauth", baidunetdisk.OAuth, dict(name="OAuth login")),
        (r"/baidunetdisk/token", baidunetdisk.Token, dict(name="get token")),
        (r"/baidunetdisk/userinfo", baidunetdisk.UserInfo, dict(name="get user info")),
        (r"/baidunetdisk/quota", baidunetdisk.Quota, dict(name="get quota")),
        (r"/baidunetdisk/sync", baidunetdisk.Sync, dict(name="sync")),
        (r"/baidunetdisk/fix", baidunetdisk.Fix, dict(name="fix")),
        (r"/baidunetdisk/download", baidunetdisk.Download, dict(name="download")),

        (r"/oss", oss.OssWebSocket),
        (r"/oss/sync", oss.Sync, dict(name="sync")),

        (r"/backup", backup.BackupWebSocket),
        (r"/backup/copy", backup.Copy, dict(name="copy")),

        (r"/check", check.CheckWebSocket),
        (r"/check/check", check.Check, dict(name="check")),

        (r"/searchfile", searchfile.SearchFileWebSocket),
        (r"/searchfile/search", searchfile.Search, dict(name="search file")),

        (r"/", error.NotFound)
    ], **options.settings)
