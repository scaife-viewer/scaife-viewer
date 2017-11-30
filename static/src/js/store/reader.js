import parseLinkHeader from 'parse-link-header';
import qs from 'query-string';
import parseURN from '../urn';


function rsplit(s, sep, maxsplit) {
  const split = s.split(sep);
  return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;
}


module.exports = {
  state: {
    textSize: 'md',
    sidebarLeftOpened: true,
    sidebarRightOpened: true,
    passage: null,
    rightPassage: null,
    versions: null,
  },
  actions: {
    async loadPassage(context, urn) {
      const pagination = {};
      const url = `/library/passage/${urn}/json/`;
      const resp = await fetch(url);
      if (resp.headers.has('link')) {
        const links = parseLinkHeader(resp.headers.get('link'));
        if (links.prev) {
          pagination.prev = {
            url: links.prev.url,
            urn: links.prev.urn,
            ref: rsplit(links.prev.urn, ':', 2).slice(-1)[0],
          };
        }
        if (links.next) {
          pagination.next = {
            url: links.next.url,
            urn: links.next.urn,
            ref: rsplit(links.next.urn, ':', 2).slice(-1)[0],
          };
        }
      }
      const passage = await resp.json();
      return { ...passage, ...pagination };
    },
    async loadVersions({ commit }, urn) {
      const url = `/library/${urn}/json/`;
      let res = await fetch(url);
      const work = await res.json();
      const e = [];
      work.texts.forEach(({ urn: textUrn }) => {
        e.push(textUrn.replace(`${work.urn}.`, ''));
      });
      const params = qs.stringify({ e });
      const textVectorUrl = `/library/vector/${work.urn}/?${params}`;
      res = await fetch(textVectorUrl);
      const vector = await res.json();
      const texts = Object.values(vector.collections);
      commit('setVersions', texts);
    },
    async setPassage({ state, dispatch, commit }, urn) {
      const p = parseURN(urn);
      if (!p.reference && state.passage) {
        const { reference: existingReference } = parseURN(state.passage.urn);
        urn = `${urn}:${existingReference}`;
      }
      await dispatch('loadVersions', `urn:${p.urnNamespace}:${p.ctsNamespace}:${p.textGroup}.${p.work}`);
      const passage = await dispatch('loadPassage', urn);
      commit('setPassage', passage);
    },
    async setPassageAndHistory({ dispatch }, urn) {
      await dispatch('setPassage', urn);
      dispatch('setHistory');
    },
    async setRightPassage({ state, dispatch, commit }, urn) {
      if (urn) {
        const p = parseURN(urn);
        if (!p.reference && state.passage) {
          const { reference: existingReference } = parseURN(state.passage.urn);
          urn = `${urn}:${existingReference}`;
        }
        commit('setRightPassage', await dispatch('loadPassage', urn));
      } else {
        commit('setRightPassage', null);
      }
    },
    async setRightPassageAndHistory({ dispatch }, urn) {
      await dispatch('setRightPassage', urn);
      dispatch('setHistory');
    },
    async setRef({ dispatch, state }, reference) {
      const pending = [];
      pending.push(dispatch('setPassage', `${state.passage.text.urn}:${reference}`));
      if (state.rightPassage) {
        pending.push(dispatch('setRightPassage', `${state.rightPassage.text.urn}:${reference}`));
      }
      return Promise.all(pending);
    },
    async setRefAndHistory({ dispatch }, urn) {
      await dispatch('setRef', urn);
      dispatch('setHistory');
    },
    setHistory({ state }) {
      const urns = [state.passage.urn];
      let location = `/reader/${state.passage.urn}/`;
      if (state.rightPassage) {
        urns.push(state.rightPassage.urn);
        const parsed = parseURN(state.rightPassage.urn);
        location += `?right=${parsed.version}`;
      }
      window.history.pushState({}, urns.join('+'), location);
    },
  },
  mutations: {
    setPassage(state, passage) {
      state.passage = passage;
    },
    setRightPassage(state, passage) {
      state.rightPassage = passage;
    },
    setVersions(state, versions) {
      state.versions = versions;
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
