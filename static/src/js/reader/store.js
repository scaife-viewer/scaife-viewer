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

function copyPassage(passage, { urn, metadata, ready, error }) {
  let newPassage;
  if (passage === null) {
    newPassage = {
      urn: null,
      metadata: null,
      ready: false,
      error: '',
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
  return newPassage;
}

module.exports = {
  namespaced: true,
  state: {
    textSize: 'md',
    sidebarLeftOpened: true,
    sidebarRightOpened: true,
    versions: null,
    leftText: null,
    rightText: null,
    leftPassage: null,
    rightPassage: null,
    selectedWord: null,
    error: '',
  },
  getters: {
    text(state) {
      return state.leftText;
    },
    passage(state) {
      return state.leftPassage;
    },
  },
  mutations: {
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
    setSelectedWord(state, payload) {
      if (payload === null) {
        state.selectedWord = null;
      } else {
        const { word } = payload;
        state.selectedWord = { ...word };
      }
    },
    setError(state, { error }) {
      state.error = error;
    },
  },
  actions: {
    load({ state, commit }, { leftUrn, rightUrn }) {
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
        ps.push(sv.fetchCollection(leftTextUrn).then((text) => {
          commit('setLeftText', { urn: leftTextUrn, metadata: text });
        }));
      }
      if (!state.leftPassage || state.leftPassage.urn.toString() !== leftUrn.toString()) {
        commit('setLeftPassage', { urn: leftUrn, ready: false, error: '' });
        ps.push(sv.fetchPassage(leftUrn)
          .then((passage) => {
            commit('setLeftPassage', { metadata: passage, ready: true });
          })
          .catch((err) => {
            commit('setLeftPassage', { error: err.toString() });
          }));
      }
      if (rightUrn) {
        const rightTextUrn = rightUrn.upTo('version');
        if (!state.rightText || state.rightText.urn.toString() !== rightTextUrn.toString()) {
          ps.push(sv.fetchCollection(rightTextUrn).then((text) => {
            commit('setRightText', { urn: rightTextUrn, metadata: text });
          }));
        }
        if (!state.rightPassage || state.rightPassage.urn.toString() !== rightUrn.toString()) {
          commit('setRightPassage', { urn: rightUrn, ready: false, error: '' });
          ps.push(sv.fetchPassage(rightUrn)
            .then((passage) => {
              commit('setRightPassage', { metadata: passage, ready: true });
            })
            .catch((err) => {
              commit('setRightPassage', { error: err.toString() });
            }));
        }
      } else if (state.rightText) {
        commit('setRightPassage', null);
      }
      return Promise.all(ps)
        .catch((err) => {
          commit('setError', { error: `failed to load reader: ${err}` });
        });
    },
    selectWord({ commit }, { word }) {
      if (word !== null) {
        commit('setSelectedWord', { word });
      } else {
        commit('setSelectedWord', null);
      }
    },
  },
};
