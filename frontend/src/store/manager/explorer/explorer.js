const explorer = {
  state: {
    explorer: {
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
