import sv, { URN } from '../scaife-viewer';

function copyText(text, { urn, metadata }) {
  let newText;
  if (text === null) {
    newText = {
      urn: null,
      metadata: null,
    }
  } else {
    newText = { ...text };
  }
  if (urn !== undefined) {
    newText.urn = urn;
  }
  if (metadata !== undefined) {
    newText.metadata = metadata;
  }
  return newText;
}

function copyPassage(passage, { urn, metadata, ready, error, redirected }) {
  let newPassage;
  if (passage === null) {
    newPassage = {
      urn: null,
      metadata: null,
      ready: false,
      error: '',
      redirected: null,
    };
  } else {
    newPassage = { ...passage };
  }
  if (urn !== undefined) {
    newPassage.urn = urn;
  }
  if (metadata !== undefined) {
    newPassage.metadata = metadata;
  }
  if (ready !== undefined) {
    newPassage.ready = ready;
  }
  if (error !== undefined) {
    newPassage.error = error;
  }
  if (redirected !== undefined) {
    newPassage.redirected = redirected;
  }
  return newPassage;
}

module.exports = {
  namespaced: true,
  state: {
    textMode: 'browser',
    textSize: 'md',
    sidebarLeftOpened: true,
    sidebarRightOpened: true,
    versions: null,
    leftText: null,
    rightText: null,
    leftPassage: null,
    rightPassage: null,
    leftPassageText: null,
    rightPassageText: null,
    highlight: null,
    annotations: new Map(),
    annotationChange: 0,
    selectedLemmas: null,
    error: '',
    selectedTokenRange: { start: null, end: null },
  },
  getters: {
    text(state) {
      return state.leftText;
    },
    passage(state) {
      return state.leftPassage;
    },
    selectedWords(state) {
      const words = [];
      const { annotations, annotationChange } = state;
      annotations.forEach((o, token) => {
        if (o.selected) {
          const [, w, i] = /^([^[]+)(?:\[(\d+)\])?$/.exec(token);
          words.push({ w, i });
        }
      });
      return words;
    },
  },
  mutations: {
    setTextMode(state, { mode }) {
      state.textMode = mode;
    },
    setTextSize(state, { size }) {
      state.textSize = size;
    },
    toggleSidebarLeft(state) {
      state.sidebarLeftOpened = !state.sidebarLeftOpened;
    },
    toggleSidebarRight(state) {
      state.sidebarRightOpened = !state.sidebarRightOpened;
    },
    setVersions(state, { versions }) {
      state.versions = versions;
    },
    setLeftText(state, payload) {
      if (payload === null) {
        state.leftText = null;
      } else {
        state.leftText = copyText(state.leftText, payload);
      }
    },
    setRightText(state, payload) {
      if (payload === null) {
        state.rightText = null;
      } else {
        state.rightText = copyText(state.rightText, payload);
      }
    },
    setLeftPassage(state, payload) {
      if (payload === null) {
        state.leftPassage = null;
      } else {
        state.leftPassage = copyPassage(state.leftPassage, payload);
      }
    },
    setRightPassage(state, payload) {
      if (payload === null) {
        state.rightPassage = null;
      } else {
        state.rightPassage = copyPassage(state.rightPassage, payload);
      }
    },
    setLeftPassageText(state, { text }) {
      state.leftPassageText = text;
    },
    setRightPassageText(state, { text }) {
      state.rightPassageText = text;
    },
    setHighlight(state, payload) {
      if (payload === null) {
        state.highlight = null;
      } else {
        const { highlight } = payload;
        state.highlight = highlight;
      }
    },
    setAnnotation(state, { token, key, value, singleton }) {
      const { annotations } = state;
      if (singleton !== undefined && singleton) {
        annotations.forEach((o) => {
          delete o[key];
        });
      }
      let ta = {};
      if (annotations.has(token)) {
        ta = annotations.get(token);
      }
      ta[key] = value;
      annotations.set(token, ta);
      state.annotationChange += 1;
    },
    setAnnotations(state, { tokens, key, value }) {
      const { annotations } = state;
      tokens.forEach((token) => {
        let ta = {};
        if (annotations.has(token)) {
          ta = annotations.get(token);
        }
        ta[key] = value;
        annotations.set(token, ta);
      });
      state.annotationChange += 1;
    },
    clearAnnotation(state, { key }) {
      const { annotations } = state;
      annotations.forEach((o) => {
        delete o[key];
      });
      state.annotationChange += 1;
    },
    setSelectedTokenRange(state, { start, end }) {
      if (start !== undefined) {
        state.selectedTokenRange.start = start;
      }
      if (end !== undefined) {
        state.selectedTokenRange.end = end;
      }
    },
    setSelectedLemmas(state, { lemmas }) {
      state.selectedLemmas = lemmas;
    },
    setError(state, { error }) {
      state.error = error;
    },
  },
  actions: {
    load({ dispatch, commit, state, rootState }, { leftUrn, rightUrn, initial = false }) {
      if (state.error) {
        commit('setError', { error: '' });
      }
      const ps = [];
      if (state.versions === null) {
        ps.push(sv.fetchCollection(leftUrn.upTo('work')).then(async (work) => {
          const texts = [];
          work.texts.forEach(({ urn }) => {
            texts.push(new URN(urn).version);
          });
          const versions = await sv.fetchCollectionVector(work.urn, texts);
          commit('setVersions', { versions });
        }));
      }
      const leftTextUrn = leftUrn.upTo('version');
      if (!state.leftText || state.leftText.urn.toString() !== leftTextUrn) {
        ps.push(sv.fetchCollection(leftTextUrn)
          .then((text) => {
            commit('setLeftText', { urn: leftTextUrn, metadata: text });
          })
          .catch((err) => {
            commit('setError', { error: err.message });
          }));
      }
      if (!state.leftPassage || state.leftPassage.urn.toString() !== leftUrn.toString()) {
        if (!initial) {
          dispatch('setSelectedToken', { token: null });
        }
        commit('setLeftPassageText', { text: null });
        commit('setLeftPassage', {
          urn: leftUrn,
          ready: false,
          error: '',
          redirected: null,
        });
        ps.push(sv.fetchPassage(leftUrn)
          .then((passage) => {
            const urn = new URN(passage.urn);
            commit('setLeftPassageText', { text: passage.text_html });
            delete passage.text_html;
            commit('setLeftPassage', { urn });
            if (leftUrn.reference !== urn.reference) {
              commit('setLeftPassage', {
                metadata: passage,
                redirected: { previousUrn: leftUrn },
                ready: true,
              });
              const { default: router } = require('../router'); // eslint-disable-line global-require
              router.push({ name: 'reader', params: { leftUrn: urn.toString() }, query: rootState.route.query });
            } else {
              commit('setLeftPassage', { metadata: passage, ready: true });
            }
          })
          .catch((err) => {
            commit('setError', { error: err.message });
          }));
      }
      if (rightUrn) {
        const rightTextUrn = rightUrn.upTo('version');
        if (!state.rightText || state.rightText.urn.toString() !== rightTextUrn.toString()) {
          ps.push(sv.fetchCollection(rightTextUrn)
            .then((text) => {
              commit('setRightText', { urn: rightTextUrn, metadata: text });
            })
            .catch((err) => {
              commit('setError', { error: err.message });
            }));
        }
        if (!state.rightPassage || state.rightPassage.urn.toString() !== rightUrn.toString()) {
          commit('setRightPassageText', { text: null });
          commit('setRightPassage', {
            urn: rightUrn,
            ready: false,
            error: '',
            redirected: null,
          });
          ps.push(sv.fetchPassage(rightUrn)
            .then((passage) => {
              const urn = new URN(passage.urn);
              commit('setRightPassageText', { text: passage.text_html });
              delete passage.text_html;
              commit('setRightPassage', { urn });
              if (rightUrn.reference !== urn.reference) {
                commit('setRightPassage', {
                  metadata: passage,
                  redirected: { previousUrn: rightUrn },
                  ready: true,
                });
              } else {
                commit('setRightPassage', { metadata: passage, ready: true });
              }
            })
            .catch((err) => {
              commit('setRightPassage', { error: err.message });
            }));
        }
      } else if (state.rightText) {
        commit('setRightPassage', null);
      }
      return Promise.all(ps)
        .then(() => {
          if (rootState.route.query.highlight && rootState.route.query.highlight !== state.highlight) {
            dispatch('highlight', {
              highlight: rootState.route.query.highlight,
              route: false,
            });
          }
        })
        .catch((err) => {
          commit('setError', { error: `failed to load reader: ${err}` });
        });
    },
    setSelectedToken({ dispatch, commit, state }, { token }) {
      commit('setSelectedTokenRange', { start: token, end: null });
      if (token === null) {
        dispatch('highlight', { highlight: null });
      } else {
        dispatch('highlight', { highlight: `@${state.selectedTokenRange.start}` });
      }
    },
    selectTokenRange({ dispatch, commit, state }, { token }) {
      if (state.selectedTokenRange.start === null) {
        const firstToken = state.leftPassage.metadata.word_tokens[0];
        const start = `${firstToken.w}[${firstToken.i}]`;
        commit('setSelectedTokenRange', { start, end: token });
      } else {
        commit('setSelectedTokenRange', { end: token });
      }
      dispatch('highlight', { highlight: `@${state.selectedTokenRange.start}-${state.selectedTokenRange.end}` });
    },
    highlight({ commit, state, rootState }, { highlight, route = true }) {
      let { query } = rootState.route;
      if (highlight !== null) {
        if (state.mode !== 'clickable') {
          commit('setTextMode', { mode: 'clickable' });
        }
        let singleton = false;
        const selectedTokens = [];
        if (highlight.indexOf('@') === -1) {
          highlight = `@${highlight}`;
        }
        if (highlight.indexOf('-') >= 0) {
          const allTokens = state.leftPassage.metadata.word_tokens;
          let [start, end] = highlight.substr(1).split('-');
          if (start.indexOf('[') === -1) {
            start = `${start}[1]`;
          }
          if (end.indexOf('[') === -1) {
            end = `${end}[1]`;
          }
          const startIdx = allTokens.findIndex(t => `${t.w}[${t.i}]` === start);
          const endIdx = allTokens.findIndex(t => `${t.w}[${t.i}]` === end);
          Array.prototype.push.apply(
            selectedTokens,
            allTokens.slice(Math.min(startIdx, endIdx), Math.max(startIdx, endIdx) + 1).map(t => `${t.w}[${t.i}]`),
          );
        } else {
          if (highlight.indexOf('[') === -1) {
            highlight = `${highlight}[1]`;
          }
          selectedTokens.push(highlight.substr(1));
          singleton = true;
        }
        selectedTokens.forEach((token) => {
          commit('setAnnotation', {
            token,
            key: 'selected',
            value: true,
            singleton,
          });
        });
        commit('setHighlight', { highlight });
        if (route) {
          query = { ...query, highlight };
        }
      } else {
        commit('clearAnnotation', { key: 'selected' });
        commit('setHighlight', null);
        if (route) {
          query = (({ highlight: deleted, ...o }) => o)(query);
        }
      }
      if (route) {
        const { default: router } = require('../router'); // eslint-disable-line global-require
        router.push({ name: 'reader', params: rootState.route.params, query });
      }
    },
  },
};
