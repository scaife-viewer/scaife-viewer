const Vue = require('vue');
const Vuex = require('vuex');

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    textGroups: [],
    allTextGroups: null,
    works: [],
    allWorks: null,
  },
  mutations: {
    setTextGroups(state, textGroups) {
      if (!state.allTextGroups) {
        state.allTextGroups = [...textGroups];
      }
      state.textGroups = textGroups;
    },
    setWorks(state, works) {
      if (!state.allWorks) {
        state.allWorks = [...works];
      }
      state.works = works;
    },
  },
  actions: {
    loadTextGroups({ commit }, url) {
      const opts = { headers: { Accept: 'application/json' } };
      return fetch(url, opts)
        .then(res => res.json())
        .then(data => data.object)
        .then((textGroups) => {
          commit('setTextGroups', textGroups);
        });
    },
    filterTextGroups({ state, commit }, query) {
      if (state.allTextGroups) {
        const textGroups = [];
        state.allTextGroups.forEach((textGroup) => {
          if (textGroup.label.toLowerCase().indexOf(query.toLowerCase()) !== -1) {
            textGroups.push(textGroup);
          }
        });
        commit('setTextGroups', textGroups);
      }
    },
    resetTextGroups({ state, commit }) {
      commit('setTextGroups', [...state.allTextGroups]);
    },
    loadWorks({ commit }, url) {
      const opts = { headers: { Accept: 'application/json' } };
      return fetch(url, opts)
        .then(res => res.json())
        .then(data => data.object)
        .then((works) => {
          commit('setWorks', works);
        });
    },
    filterWorks({ state, commit }, query) {
      if (state.allWorks) {
        const works = [];
        state.allWorks.forEach((work) => {
          if (work.label.toLowerCase().indexOf(query.toLowerCase()) !== -1) {
            works.push(work);
          }
        });
        commit('setWorks', works);
      }
    },
    resetWorks({ state, commit }) {
      commit('setWorks', [...state.allWorks]);
    },
  },
});

export default store;
