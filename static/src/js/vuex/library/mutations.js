import constants from '../../constants';

export default {
  [constants.SET_TEXT_GROUPS]: (state, { textGroups, works, texts }) => {
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

  [constants.SET_TEXT_GROUP_URNS]: (state, { textGroupUrns }) => {
    state.textGroupUrns = textGroupUrns;
  },

  [constants.SET_LIBRARY_SORT]: (state, { kind }) => {
    state.sortKind = kind;
  },

  [constants.SET_WORKS]: (state, works) => {
    if (!state.allWorks) {
      state.allWorks = [...works];
    }
    state.works = works;
  },

  [constants.SET_VERSIONS]: (state, versions) => {
    state.versions = versions;
  },

  [constants.SET_TOC]: (state, toc) => {
    state.toc = toc;
  },
};
