export default {
  text(state) {
    return state.leftText;
  },
  passage(state) {
    return state.leftPassage;
  },
  selectedWords2(state) {
    const words = [];
    Object.keys(state.annotationsHash).forEach((token) => {
      if (state.annotationsHash[token].selected) {
        const [, w, i] = /^([^[]+)(?:\[(\d+)\])?$/.exec(token);
        words.push({ w, i });
      }
    });
    return words;
  },
  selectedWords(state) {
    const words = [];
    const { annotations } = state;
    annotations.forEach((o, token) => {
      if (o.selected) {
        const [, w, i] = /^([^[]+)(?:\[(\d+)\])?$/.exec(token);
        words.push({ w, i });
      }
    });
    return words;
  },
  textToc(state) {
    return state.leftText.metadata.toc;
  },
};
