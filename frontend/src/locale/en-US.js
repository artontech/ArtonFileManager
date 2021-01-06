const all = {
  done: "Done",
  import: "Import",
  info: "info",
  select_all: "Select All",
  warning: "warning",
  download: "Downlaod",
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
  root_dir: "Root",
  move_to: "Move to",
  delete: "Delete",
  rename: "Rename",
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
    title: "Edit tag",
    select1_placeholder: "select or input your tag",
  },
  file_list: {
  },
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
};

const menu = {
  setting: "Setting",
  manager: "Manager",
  repository: "Repository",
  explorer: "Explorer",
  dropdown_menu: {
    label1_caption: "Id",
    label2_caption: "Space",
    label3_caption: "Files",
    label4_caption: "Directories",
  },
};

const repository = {
  edit1_addonbefore: "Repository",
  edit1_placeholder: "repository path",
  btn1_caption: "Init",
  label1_caption: "Enable",
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
  }
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

export { all, explorer, menu, repository, setting, websocket };
