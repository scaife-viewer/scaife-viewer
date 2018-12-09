import * as sv from '../../scaife-viewer';

const { URN } = sv;

export default {
  load({ dispatch, commit, state, rootState }, { leftUrn, rightUrn, query, initial = false }) {
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
            // @@@
            // const { default: router } = require('../router'); // eslint-disable-line global-require
            // router.push({ name: 'reader', params: { leftUrn: urn.toString() }, query: rootState.route.query });
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
        if (query.highlight && query.highlight !== state.highlight) {
          dispatch('highlight', {
            highlight: query.highlight,
            route: false,
          });
        }
      });
      // .catch((err) => {
      //   commit('setError', { error: `failed to load reader: ${err}` });
      // });
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
    // @@@
    if (route) {
      // const { default: router } = require('../router'); // eslint-disable-line global-require
      // router.push({ name: 'reader', params: rootState.route.params, query });
    }
  },
};
