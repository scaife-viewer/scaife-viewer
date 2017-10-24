

module.exports = {
  state: {
    textSize: 'md',
    sidebarLeftOpened: true,
    sidebarRightOpened: true,
    passages: new Map(),
  },
  actions: {
    async loadPassages({ commit }, urns) {
      await Promise.all(urns.map(async (urn) => {
        const url = `http://localhost:3000/library/passage/${urn}/`;
        const resp = await fetch(url);
        const passage = await resp.json();
        commit('addPassage', passage);
      }));
    },
  },
  mutations: {
    addPassage(state, passage) {
      state.passages.set(passage.urn, passage);
    },
    toggleSidebarLeft(state) {
      state.sidebarLeftOpened = !state.sidebarLeftOpened;
    },
    toggleSidebarRight(state) {
      state.sidebarRightOpened = !state.sidebarRightOpened;
    },
  },
};
