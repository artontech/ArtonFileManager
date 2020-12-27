const explorer = {
  state: {
    explorer: {
      breadcrumb_max_len: 5, // Max len of breadcrumb before fold
      nocache: undefined, // Nocache content
    },
  },
  mutations: {
    updateExplorer(state, payload) {
      Object.assign(state.explorer, payload);
    },
    updateExplorerNocache(state, payload) {
      if (state.explorer.nocache) {
        Object.assign(state.explorer.nocache, payload);
      } else {
        state.explorer.nocache = payload;
      }
    },
  },
};

export default explorer;
