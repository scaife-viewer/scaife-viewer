import api from '../../api';
import constants from '../../constants';
import URN from '../../urn';

export default {
  [constants.READER_LOAD]: ({ dispatch, commit, state }, {
    leftUrn,
    rightUrn,
    query,
    initial,
  }) => {
    if (state.error) {
      commit(constants.SET_ERROR, { error: '' });
    }
    const ps = [];
    if (state.versions === null) {
      ps.push(
        api.getCollection(leftUrn.upTo('work'), (work) => {
          const texts = work.texts.map((text) => {
            return new URN(text.urn).version;
          });
          api.getLibraryVector(work.urn, texts, (versions) => {
            commit(constants.SET_VERSIONS, { versions });
          });
        }),
      );
    }

    const leftTextUrn = leftUrn.upTo('version');
    if (!state.leftText || state.leftText.urn.toString() !== leftTextUrn) {
      ps.push(
        api.getCollection(leftTextUrn, (text) => {
          commit(constants.SET_LEFT_TEXT, { urn: leftTextUrn, metadata: text });
        }).catch(err => commit(constants.SET_ERROR, { error: err.message })),
      );
    }
    if (!state.leftPassage || state.leftPassage.urn.toString() !== leftUrn.toString()) {
      if (!initial) {
        dispatch(constants.READER_SET_SELECTED_TOKEN, { token: null });
      }
      commit(constants.SET_LEFT_PASSAGE_TEXT, { text: null });
      commit(constants.SET_LEFT_PASSAGE, {
        urn: leftUrn,
        ready: false,
        error: '',
        redirected: null,
      });
      ps.push(
        api.getPassage(leftUrn, (passage) => {
          const urn = new URN(passage.urn);
          commit(constants.SET_LEFT_PASSAGE_TEXT, { text: passage.text_html });
          delete passage.text_html;
          commit(constants.SET_LEFT_PASSAGE, { urn });
          if (leftUrn.reference !== urn.reference) {
            commit(constants.SET_LEFT_PASSAGE, {
              metadata: passage,
              redirected: { previousUrn: leftUrn },
              ready: true,
            });
            // @@@
            // const { default: router } = require('../router'); // eslint-disable-line global-require
            // router.push({ name: 'reader', params: { leftUrn: urn.toString() }, query: rootState.route.query });
          } else {
            commit(constants.SET_LEFT_PASSAGE, { metadata: passage, ready: true });
          }
        }).catch((err) => {
          commit(constants.SET_ERROR, { error: err.message });
        }),
      );
    }

    if (rightUrn) {
      const rightTextUrn = rightUrn.upTo('version');
      if (!state.rightText || state.rightText.urn.toString() !== rightTextUrn.toString()) {
        ps.push(
          api.getCollection(rightTextUrn, (text) => {
            commit(constants.SET_RIGHT_TEXT, { urn: rightTextUrn, metadata: text });
          }).catch((err) => {
            commit(constants.SET_ERROR, { error: err.message });
          }),
        );
      }

      if (!state.rightPassage || state.rightPassage.urn.toString() !== rightUrn.toString()) {
        commit(constants.SET_RIGHT_PASSAGE_TEXT, { text: null });
        commit(constants.SET_RIGHT_PASSAGE, {
          urn: rightUrn,
          ready: false,
          error: '',
          redirected: null,
        });
        ps.push(
          api.getPassage(rightUrn, (passage) => {
            const urn = new URN(passage.urn);
            commit(constants.SET_RIGHT_PASSAGE_TEXT, { text: passage.text_html });
            delete passage.text_html;
            commit(constants.SET_RIGHT_PASSAGE, { urn });
            if (rightUrn.reference !== urn.reference) {
              commit(constants.SET_RIGHT_PASSAGE, {
                metadata: passage,
                redirected: { previousUrn: rightUrn },
                ready: true,
              });
            } else {
              commit(constants.SET_RIGHT_PASSAGE, { metadata: passage, ready: true });
            }
          }).catch((err) => {
            commit(constants.SET_RIGHT_PASSAGE, { error: err.message });
          }),
        );
      }
    } else if (state.rightText) {
      commit(constants.SET_RIGHT_PASSAGE, null);
    }
    return Promise.all(ps).then(() => {
      if (query.highlight && query.highlight !== state.highlight) {
        dispatch(constants.READER_HIGHLIGHT, {
          highlight: query.highlight,
          route: false,
        });
      }
    }).catch((err) => {
      commit(constants.SET_ERROR, { error: `failed to load reader: ${err}` });
    });
  },

  [constants.READER_SET_SELECTED_TOKEN]: ({ dispatch, commit, state }, { token }) => {
    commit(constants.SET_SELECTED_TOKEN_RANGE, { start: token, end: null });
    if (token === null) {
      dispatch(constants.READER_HIGHLIGHT, { highlight: null });
    } else {
      dispatch(constants.READER_HIGHLIGHT, { highlight: `@${state.selectedTokenRange.start}` });
    }
  },

  [constants.READER_SELECT_TOKEN_RANGE]: ({ dispatch, commit, state }, { token }) => {
    if (state.selectedTokenRange.start === null) {
      const firstToken = state.leftPassage.metadata.word_tokens[0];
      const start = `${firstToken.w}[${firstToken.i}]`;
      commit(constants.SET_SELECTED_TOKEN_RANGE, { start, end: token });
    } else {
      commit(constants.SET_SELECTED_TOKEN_RANGE, { end: token });
    }
    dispatch(constants.READER_HIGHLIGHT, { highlight: `@${state.selectedTokenRange.start}-${state.selectedTokenRange.end}` });
  },

  [constants.READER_HIGHLIGHT]: ({ commit, state, rootState }, { highlight, route = true }) => {
    let { query } = rootState.route;
    if (highlight !== null) {
      if (state.mode !== 'clickable') {
        commit(constants.SET_TEXT_MODE, { mode: 'clickable' });
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
        commit(constants.SET_ANNOTATION, {
          token,
          key: 'selected',
          value: true,
          singleton,
        });
      });
      commit(constants.SET_HIGHLIGHT, { highlight });
      if (route) {
        query = { ...query, highlight };
      }
    } else {
      commit(constants.CLEAR_ANNOTATION, { key: 'selected' });
      commit(constants.SET_HIGHLIGHT, null);
      if (route) {
        query = (({ highlight: deleted, ...o }) => o)(query);
      }
    }
    // @@@ Should set the route, I guess.  Nothing in Vuex should control routing
    if (route) {
      // const { default: router } = require('../router'); // eslint-disable-line global-require
      // router.push({ name: 'reader', params: rootState.route.params, query });
    }
  },
};
