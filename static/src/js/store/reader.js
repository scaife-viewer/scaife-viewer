import parseLinkHeader from 'parse-link-header';


module.exports = {
  state: {
    textSize: 'md',
    sidebarLeftOpened: true,
    sidebarRightOpened: true,
    passage: null,
  },
  actions: {
    async setPassage({ commit }, urn) {
      const pagination = {};
      const url = `/library/passage/${urn}/json/`;
      const resp = await fetch(url);
      if (resp.headers.has('link')) {
        const links = parseLinkHeader(resp.headers.get('link'));
        if (links.prev) {
          pagination.prev = { url: links.prev.url, urn: links.prev.urn };
        }
        if (links.next) {
          pagination.next = { url: links.next.url, urn: links.next.urn };
        }
      }
      const passage = await resp.json();
      commit('setPassage', { ...passage, ...pagination });
    },
  },
  mutations: {
    setPassage(state, passage) {
      state.passage = passage;
    },
    setTextSize(state, size) {
      state.textSize = size;
    },
    toggleSidebarLeft(state) {
      state.sidebarLeftOpened = !state.sidebarLeftOpened;
    },
    toggleSidebarRight(state) {
      state.sidebarRightOpened = !state.sidebarRightOpened;
    },
  },
};
