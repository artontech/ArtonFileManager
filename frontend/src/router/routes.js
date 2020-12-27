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
    path: "/repository",
    name: "Repository",
    component: () => import("../views/manager/repository/Repository.vue"),
  },
];

export default routes;