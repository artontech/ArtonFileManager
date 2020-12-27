import Vue from "vue";
import Vuex from "vuex";
import persistedState from "vuex-persistedstate";

import explorer from "./manager/explorer/explorer";
import repository from "./manager/repository";
import setting from "./setting";

Vue.use(Vuex);

const options = {
  plugins: [
    persistedState({
      storage: {
        getItem: (key) => {
          return localStorage.getItem(key);
        },
        setItem: (key, value) => {
          let obj = JSON.parse(value);
          if (obj.explorer) {
            delete obj.explorer.nocache;
          }
          if (obj.setting) {
            delete obj.setting.nocache;
          }
          localStorage.setItem(key, JSON.stringify(obj));
        },
        removeItem: (key) => {
          localStorage.removeItem(key);
        },
      },
    }),
  ],
  state: {
    ...explorer.state,
    ...repository.state,
    ...setting.state,
  },
  mutations: {
    ...explorer.mutations,
    ...repository.mutations,
    ...setting.mutations,
  },
};

const store = new Vuex.Store(options);

export default store;
