export default {
  setTextGroups(state, { textGroups, works, texts }) {
    if (textGroups !== undefined) {
      if (!state.allTextGroups) {
        state.allTextGroups = [...textGroups];
      }
      state.textGroups = textGroups;
    }
    if (works !== undefined) {
      if (!state.allTextGroupWorks) {
        state.allTextGroupWorks = [...works];
      }
      state.textGroupWorks = works;
    }
    if (texts !== undefined) {
      if (!state.allTextGroupTexts) {
        state.allTextGroupTexts = [...texts];
      }
      state.textGroupTexts = texts;
    }
  },
  setTextGroupUrns(state, { textGroupUrns }) {
    state.textGroupUrns = textGroupUrns;
  },
  setLibrarySort(state, { kind }) {
    state.sortKind = kind;
  },
  setWorks(state, works) {
    if (!state.allWorks) {
      state.allWorks = [...works];
    }
    state.works = works;
  },
  setToc(state, toc) {
    state.toc = toc;
  }
};
