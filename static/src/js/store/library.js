import qs from 'query-string';

module.exports = {
  state: {
    textGroups: [],
    allTextGroups: null,
    works: [],
    allWorks: null,
    toc: [],
  },
  actions: {
    loadTextGroups({ commit }) {
      const url = '/library/json/';
      const opts = { headers: { Accept: 'application/json' } };
      return fetch(url, opts)
        .then(res => res.json())
        .then(data => data.text_groups)
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
    async loadWorkList({ commit }, textGroupUrl) {
      let params;
      let res;
      let vector;

      const opts = { headers: { Accept: 'application/json' } };
      res = await fetch(textGroupUrl, opts);
      const textGroup = await res.json();

      // To reduce the load on the API, we prepare two vector calls against works
      // and texts.

      // vector for works
      params = qs.stringify({
        e: textGroup.works.map(work => work.urn.replace(`${textGroup.urn}.`, '')),
      });
      const workVectorUrl = `/library/vector/${textGroup.urn}/?${params}`;
      res = await fetch(workVectorUrl);
      vector = await res.json();
      const workMap = vector.collections;

      // vector for texts
      const e = [];
      textGroup.works.forEach(({ urn: workUrn }) => {
        const work = workMap[workUrn];
        work.texts.forEach(({ urn: textUrn }) => {
          e.push(textUrn.replace(`${textGroup.urn}.`, ''));
        });
      });
      params = qs.stringify({ e });
      const textVectorUrl = `/library/vector/${textGroup.urn}/?${params}`;
      res = await fetch(textVectorUrl);
      vector = await res.json();
      const textMap = vector.collections;

      // finally prepare the works object to store
      const works = [];
      textGroup.works.forEach(({ urn: workUrn }) => {
        const work = workMap[workUrn];
        works.push({
          ...work,
          texts: work.texts.map(({ urn: textUrn }) => textMap[textUrn]),
        });
      });

      commit('setWorks', works);
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
    async loadTocList({ commit }, textUrl) {
      const opts = { headers: { Accept: 'application/json' } };
      const res = await fetch(textUrl, opts);
      const text = await res.json();
      commit('setToc', text.toc);
    },
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
    setToc(state, toc) {
      state.toc = toc;
    },
  },
};
