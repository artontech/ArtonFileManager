const all = {
  done: "完成",
  import: "导入",
  info: "消息",
  select_all: "全选",
  warning: "警告",
  download: "下载",
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
    title: "编辑标签",
    select1_placeholder: "选择或输入标签",
  },
  file_list: {
  },
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
};

const menu = {
  setting: "设置",
  manager: "文件资源管理器",
  repository: "管理仓库",
  explorer: "浏览文件",
  dropdown_menu: {
    label1_caption: "占用空间",
    label2_caption: "文件数",
    label3_caption: "文件夹数",
  },
};

const repository = {
  edit1_addonbefore: "仓库路径",
  edit1_placeholder: "请填写仓库路径",
  btn1_caption: "创建",
  label1_caption: "启用仓库",
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
  }
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

export { all, explorer, menu, repository, setting, websocket };
