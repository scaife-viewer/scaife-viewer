import constants from '../../constants';

function copyText(text, { urn, metadata }) {
  let newText;
  if (text === null) {
    newText = {
      urn: null,
      metadata: null,
    };
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

function copyPassage(passage, {
  urn, metadata, ready, error, redirected,
}) {
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

export default {
  [constants.SET_TEXT_MODE]: (state, { mode }) => {
    state.textMode = mode;
  },

  [constants.READER_TOGGLE_SIDEBAR_LEFT]: (state) => {
    state.sidebarLeftOpened = !state.sidebarLeftOpened;
  },

  [constants.READER_TOGGLE_SIDEBAR_RIGHT]: (state) => {
    state.sidebarRightOpened = !state.sidebarRightOpened;
  },

  [constants.SET_VERSIONS]: (state, { versions }) => {
    state.versions = versions;
  },

  [constants.SET_LEFT_TEXT]: (state, payload) => {
    if (payload === null) {
      state.leftText = null;
    } else {
      state.leftText = copyText(state.leftText, payload);
    }
  },

  [constants.SET_RIGHT_TEXT]: (state, payload) => {
    if (payload === null) {
      state.rightText = null;
    } else {
      state.rightText = copyText(state.rightText, payload);
    }
  },

  [constants.SET_LOWER_TEXT]: (state, payload) => {
    if (payload === null) {
      state.lowerText = null;
    } else {
      state.lowerText = copyText(state.lowerText, payload);
    }
  },

  [constants.SET_LEFT_PASSAGE]: (state, payload) => {
    if (payload === null) {
      state.leftPassage = null;
    } else {
      state.leftPassage = copyPassage(state.leftPassage, payload);
    }
  },

  [constants.SET_RIGHT_PASSAGE]: (state, payload) => {
    if (payload === null) {
      state.rightPassage = null;
    } else {
      state.rightPassage = copyPassage(state.rightPassage, payload);
    }
  },

  [constants.SET_LOWER_PASSAGE]: (state, payload) => {
    if (payload === null) {
      state.lowerPassage = null;
    } else {
      state.lowerPassage = copyPassage(state.lowerPassage, payload);
    }
  },

  [constants.SET_LEFT_PASSAGE_TEXT]: (state, { text }) => {
    state.leftPassageText = text;
  },

  [constants.SET_RIGHT_PASSAGE_TEXT]: (state, { text }) => {
    state.rightPassageText = text;
  },

  [constants.SET_LOWER_PASSAGE_TEXT]: (state, { text }) => {
    state.lowerPassageText = text;
  },

  [constants.SET_HIGHLIGHT]: (state, payload) => {
    if (payload === null) {
      state.highlight = null;
    } else {
      const { highlight } = payload;
      state.highlight = highlight;
    }
  },

  [constants.SET_ANNOTATION]: (state, {
    token, key, value, singleton,
  }) => {
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

    if (singleton !== undefined && singleton && key === 'selected') {
      // set all selected keys to false
      const c = { ...state.annotationsHash };
      Object.keys(state.annotationsHash).forEach((k) => {
        c[k].selected = false;
      });
      state.annotationsHash = { ...c };
    }
    state.annotationsHash = {
      ...state.annotationsHash,
      [token]: {
        ...state.annotationsHash[token],
        [key]: value,
      },
    };

    state.annotationChange += 1;
  },

  [constants.SET_ANNOTATIONS]: (state, { tokens, key, value }) => {
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

  [constants.CLEAR_ANNOTATION]: (state, { key }) => {
    const { annotations } = state;
    annotations.forEach((o) => {
      delete o[key];
    });
    state.annotationChange += 1;
  },

  [constants.SET_SELECTED_TOKEN_RANGE]: (state, { start, end }) => {
    if (start !== undefined) {
      state.selectedTokenRange.start = start;
    }
    if (end !== undefined) {
      state.selectedTokenRange.end = end;
    }
  },

  [constants.READER_SET_SELECTED_LEMMAS]: (state, { lemmas }) => {
    state.selectedLemmas = lemmas;
  },

  [constants.SET_ERROR]: (state, { error }) => {
    state.error = error;
  },

};
