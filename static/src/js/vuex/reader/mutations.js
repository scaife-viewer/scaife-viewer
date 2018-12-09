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

export default {
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
};
