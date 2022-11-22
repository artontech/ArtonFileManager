import Setting from "../views/setting/Setting.vue";

const routes = [
  {
    path: "/",
    name: "Setting",
    component: Setting,
  },
  {
    path: "/explorer",
    name: "Explorer",
    // route level code-splitting
    // this generates a separate chunk (module_name.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import("../views/manager/explorer/Explorer.vue"),
  },
  {
    path: "/backup",
    name: "Backup",
    component: () => import("../views/manager/Backup.vue"),
  },
  {
    path: "/check",
    name: "Check",
    component: () => import("../views/manager/Check.vue"),
  },
  {
    path: "/repository",
    name: "Repository",
    component: () => import("../views/manager/repository/Repository.vue"),
  },
  {
    path: "/searchfile",
    name: "SearchFile",
    component: () => import("../views/manager/SearchFile.vue"),
  },
  {
    path: "/baidumanager",
    name: "BaiduManager",
    component: () => import("../views/netdisk/baidunetdisk/BaiduManager.vue"),
  },
  {
    path: "/baidusync",
    name: "BaiduSync",
    component: () => import("../views/netdisk/baidunetdisk/BaiduSync.vue"),
  },
  {
    path: "/baidufix",
    name: "BaiduFix",
    component: () => import("../views/netdisk/baidunetdisk/BaiduFix.vue"),
  },
  {
    path: "/osssync",
    name: "OssSync",
    component: () => import("../views/netdisk/oss/OssSync.vue"),
  },
];

export default routes;