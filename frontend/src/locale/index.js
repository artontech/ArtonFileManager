import Vue from "vue";

import VueI18n from "vue-i18n";

Vue.use(VueI18n);

const messages = {
  "zh-CN": require("./zh-CN"),
  "en-US": require("./en-US"),
};

const i18n = new VueI18n({
  locale: "zh-CN",
  messages,
});

export default i18n;
