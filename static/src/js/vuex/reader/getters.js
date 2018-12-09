export default {
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
};
