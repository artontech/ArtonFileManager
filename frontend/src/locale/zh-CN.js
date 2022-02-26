const all = {
  done: "完成",
  import: "导入",
  export: "导出",
  info: "消息",
  select_all: "全选",
  warning: "警告",
  download: "下载",
  upload: "上传",
  tag: "标签",
  add: "添加",
  open: "打开",
  edit: "编辑",
  select: "选择",
  icon: "图标",
  name: "名称",
  size: "大小",
  action: "操作",
  detail: "详情",
  mkdir: "新建文件夹",
  ok: "确认",
  cancel: "取消",
  root_dir: "根目录",
  move_to: "移动到",
  delete: "删除",
  rename: "重命名",
  clear: "清空",
};

const explorer = {
  import_drawer: {
    title: "导入目录",
    edit1_placeholder: "请填写要导入的路径",
    label1_caption: "进度",
    tooltip1_caption: "导入目录结构进度",
    progress1_caption: "导入目录",
    tooltip2_caption: "导入文件进度",
    progress2_caption: "导入文件",
    label2_caption: "日志",
  },
  tag_drawer: {
    download_baidu: "从百度网盘下载",
    download_fail: "下载失败",
    download_oss: "从OSS下载",
    title: "编辑标签",
    select1_placeholder: "选择或输入标签",
  },
  upload_drawer: {
    title: "上传文件",
    label1_caption: "文件列表",
    btn3_caption: "清空重复",
    table1: {
      name: "文件名",
      dup: "文件重复",
      action: "操作",
    },
    upload_hint: "支持单文件及批量上传",
    upload_text: "把文件拖入此区域，或点击进行上传",
  },
  file_list: {},
  dir_input: {
    title: "请输入文件夹名称",
    placeholder: "文件夹名称",
  },
  dir_selector: {
    title: "请选择一个文件夹",
  },
  rename: {
    title: "请输入新名称",
    placeholder: "新名称",
  },
  export: {
    title: "导出到",
    placeholder: "请输入文件夹路径",
  },
  export_done: "导出成功",
  export_fail: "导出失败",
};

const menu = {
  setting: "设置",
  manager: "文件资源管理器",
  repository: "管理仓库",
  explorer: "浏览文件",
  netdisk: "网盘",
  baidunetdisk: "百度网盘",
  baidumanager: "网盘管理",
  baidusync: "网盘同步",
  baidufix: "网盘修复",
  oss: "阿里云OSS",
  osssync: "OSS同步",
  dropdown_menu: {
    label1_caption: "编号",
    label2_caption: "占用空间",
    label3_caption: "文件数",
    label4_caption: "文件夹数",
  },
};

const repository = {
  edit1_addonbefore: "仓库路径",
  edit1_placeholder: "请填写仓库路径",
  btn1_caption: "创建",
  label1_caption: "启用仓库",
  password_input: {
    title: "请设置仓库密码",
    placeholder: "仓库密码",
  },
};

const setting = {
  tab1: "基础设置",
  tab2: "文件浏览",
  basic: {
    label1: "服务器地址：",
    label2: "加密方式：",
    edit1_placeholder: "服务器地址",
    edit2_placeholder: "加密方式",
    btn1_caption: "连接",
  },
  explorer: {
    checkbox1: "显示图片缩略图",
    checkbox2: "缓存图片",
    label1: "导出路径：",
    edit1_placeholder: "导出路径",
  },
};

const websocket = {
  attr_fail: "获取文件属性失败",
  dup_file: "文件已存在",
  io_error: "出现IO错误",
  structure_done: "获取目录结构完成",
  structure_fail: "获取目录结构失败",
  load_img_fail: "加载图片失败",
  calc_hash_fail: "计算图片哈希失败",
  import_done: "导入成功",
};

const baidunetdisk = {
  baidumanager: {
    label1_caption: "连接到网盘",
    btn1_caption: "登录",
  },
  baidusync: {
    btn1_caption: "同步",
    label1_caption: "进度",
    tooltip1_caption: "检查进度",
    progress1_caption: "检查",
    tooltip2_caption: "上传进度",
    progress2_caption: "上传",
  },
  baidufix: {
    btn1_caption: "修复",
    label1_caption: "进度",
    tooltip1_caption: "检查进度",
    progress1_caption: "检查",
    tooltip2_caption: "修复进度",
    progress2_caption: "修复",
  },
};

const oss = {
  osssync: {
    btn1_caption: "同步",
    label1_caption: "进度",
    tooltip1_caption: "检查进度",
    progress1_caption: "检查",
    tooltip2_caption: "上传进度",
    progress2_caption: "上传",
  },
};

export { all, explorer, menu, repository, setting, websocket, baidunetdisk, oss };
