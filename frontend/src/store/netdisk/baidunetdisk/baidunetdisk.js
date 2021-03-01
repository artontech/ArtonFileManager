function assign(obj, key, value) {
  if (obj[key]) {
    Object.assign(obj[key], value);
  } else {
    obj[key] = value;
  }
}

const baidunetdisk = {
  state: {
    baidunetdisk: {
      nocache: {
        info: null,
      },
    },
  },
  mutations: {
    updateBaiduNetdisk(state, payload) {
      assign(state, "baidunetdisk", payload);
    },
    updateBaiduNetdiskNocache(state, payload) {
      assign(state.baidunetdisk, "nocache", payload);
    },
  },
};

export default baidunetdisk;
