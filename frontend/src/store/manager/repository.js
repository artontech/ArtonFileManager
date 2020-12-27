const repository = {
  state: {
    repository: {
      init: false,
      loaded: false,
      path: "",
      wid: 0,
    },
  },
  mutations: {
    updateRepository(state, payload) {
      state.repository = {
        ...state.repository,
        ...payload,
      };
    },
  },
};

export default repository;
