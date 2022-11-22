const all = {
  done: "Done",
  import: "Import",
  export: "Export",
  info: "info",
  select_all: "Select All",
  warning: "warning",
  download: "Downlaod",
  upload: "Upload",
  tag: "Tag",
  add: "Add",
  open: "Open",
  edit: "Edit",
  select: "Select",
  icon: "Icon",
  name: "Name",
  size: "Size",
  action: "Action",
  detail: "Detail",
  mkdir: "Create Dir",
  ok: "OK",
  cancel: "Cancel",
  canceling: "Canceling",
  canceled: "Canceled",
  root_dir: "Root",
  move_to: "Move to",
  delete: "Delete",
  rename: "Rename",
  clear: "Clear",
  param_invalid: "Param invalid",
  result: "Result",
  hide: "Hide",
  home: "Home",
  back: "Back",
  ahash: "aHash",
  dhash: "dHash",
  phash: "pHash",
  attr_id: "AttrId",
};

const explorer = {
  import_drawer: {
    title: "Import",
    edit1_placeholder: "input the path to import",
    label1_caption: "progress",
    tooltip1_caption: "import structure",
    progress1_caption: "structure",
    tooltip2_caption: "import files",
    progress2_caption: "file",
    label2_caption: "logging",
  },
  tag_drawer: {
    download_baidu: "Baidu Download",
    download_fail: "Download failed",
    download_oss: "OSS Download",
    title: "Edit tag",
    select1_placeholder: "select or input your tag",
  },
  upload_drawer: {
    title: "Upload file",
    label1_caption: "File list",
    btn3_caption: "Clear duplicated",
    table1: {
      name: "File name",
      dup: "Dup file",
      action: "Action",
    },
    upload_hint: "Support for a single or bulk upload.",
    upload_text: "Click or drag file to this area to upload",
  },
  file_list: {},
  dir_input: {
    title: "Input directory name",
    placeholder: "Directory name",
  },
  dir_selector: {
    title: "Select a dir",
  },
  rename: {
    title: "Input new name",
    placeholder: "New name",
  },
  export: {
    title: "Export to",
    placeholder: "Input target dir path",
  },
  export_done: "Export succeed",
  export_fail: "Export failed",
};

const menu = {
  setting: "Setting",
  manager: "Manager",
  repository: "Repository",
  explorer: "Explorer",
  backup: "Backup",
  check: "Check",
  netdisk: "Netdisk",
  baidunetdisk: "Baidu Netdisk",
  baidumanager: "Baidu Manager",
  baidusync: "Baidu Sync",
  baidufix: "Baidu Fix",
  oss: "OSS",
  osssync: "OSS Sync",
  dropdown_menu: {
    label1_caption: "Id",
    label2_caption: "Space",
    label3_caption: "Files",
    label4_caption: "Directories",
  },
  search_file: "Search File",
};

const backup = {
  btn1_caption: "Backup",
  edit1_placeholder: "backup path",
  label1_caption: "Progress",
  label2_caption: "Log",
  tooltip1_caption: "check progress",
  progress1_caption: "check",
  tooltip2_caption: "backup progress",
  progress2_caption: "backup",
};

const check = {
  btn1_caption: "Check",
  label1_caption: "Progress",
  label2_caption: "Log",
  tooltip1_caption: "prepare progress",
  progress1_caption: "prepare",
  tooltip2_caption: "check progress",
  progress2_caption: "check",
  no_check_date: "Please select a date",
};

const repository = {
  edit1_addonbefore: "Repository",
  edit1_placeholder: "repository path",
  btn1_caption: "Init",
  label1_caption: "Enable",
  password_input: {
    title: "Set repository password",
    placeholder: "Repository password",
  },
};

const setting = {
  tab1: "Basic",
  tab2: "Explorer",
  basic: {
    label1: "Server address:",
    label2: "Encrypt type:",
    edit1_placeholder: "server address",
    edit2_placeholder: "encrypt type",
    btn1_caption: "Connect",
  },
  explorer: {
    checkbox1: "Show picture preview",
    checkbox2: "Cache picture",
    label1: "Export path:",
    edit1_placeholder: "export path",
  },
};

const search_file = {
  btn1_caption: "Search",
  input1_placeholder: "aHash",
  input2_placeholder: "dHash",
  input3_placeholder: "pHash",
  input4_placeholder: "AttrId",
  view_dir: "view dir",
};

const websocket = {
  attr_fail: "failed to get file attr",
  dup_file: "file exists",
  io_error: "IO error",
  structure_done: "get structure done",
  structure_fail: "failed to get structure",
  load_img_fail: "failed to load image",
  calc_hash_fail: "failed to calc pic hash",
  import_done: "import done",
};

const baidunetdisk = {
  baidumanager: {
    label1_caption: "Connect",
    btn1_caption: "Login",
  },
  baidusync: {
    btn1_caption: "Sync",
    label1_caption: "Progress",
    tooltip1_caption: "check progress",
    progress1_caption: "check",
    tooltip2_caption: "upload progress",
    progress2_caption: "upload",
  },
  baidufix: {
    btn1_caption: "Fix",
    label1_caption: "Progress",
    tooltip1_caption: "check progress",
    progress1_caption: "check",
    tooltip2_caption: "fix progress",
    progress2_caption: "fix",
  },
};

const oss = {
  osssync: {
    btn1_caption: "Sync",
    label1_caption: "Progress",
    tooltip1_caption: "check progress",
    progress1_caption: "check",
    tooltip2_caption: "upload progress",
    progress2_caption: "upload",
  },
};

export {
  all,
  explorer,
  menu,
  backup,
  check,
  repository,
  search_file,
  setting,
  websocket,
  baidunetdisk,
  oss
};
