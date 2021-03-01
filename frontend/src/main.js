import Vue from "vue";
import VueResource from "vue-resource";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/antd.css";

import App from "./App.vue";
import i18n from "./locale";
import router from "./router";
import routes from "@/router/routes.js";
import store from "./store";

Vue.use(VueResource);
Vue.use(Antd);
Vue.config.productionTip = false;

router.go = (target, param) => {
  routes.forEach((element) => {
    if (element.name === target) {
      if (param) {
        router.push(`${element.path}?${param}`);
      } else {
        router.push(element.path);
      }
    }
  });
};

new Vue({
  i18n,
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
