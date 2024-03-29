const setting = {
  state: {
    setting: {
      address: "localhost:13310", // Api server address
      delete: false, // Delete file after import done
      encrypt: "AES", // Default encrypt algo
      showthumb: true, // Show pic thumb or not
      cachethumb: false, // Cache thumb or not
      chunklimit: 10, // Limit video thumb chunk count
      thumbtype: "gif", // Video thumb type
      exportpath: "", // Export path
      nocache: undefined, // Nocache content
    },
  },
  mutations: {
    updateSetting(state, payload) {
      Object.assign(state.setting, payload);
    },
    updateSettingNocache(state, payload) {
      if (state.setting.nocache) {
        Object.assign(state.setting.nocache, payload);
      } else {
        state.setting.nocache = payload;
      }
    },
  },
};

export default setting;
