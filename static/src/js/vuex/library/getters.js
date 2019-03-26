export default {
  hydratedTextGroups(state) {
    return state.textGroups.map(textGroup => ({
      ...textGroup,
      urn: textGroup.urn.toString(),
      works: textGroup.works.map(work => ({
        ...state.textGroupUrns[work.urn.toString()],
        urn: work.urn.toString(),
        texts: work.texts.map(text => ({
          ...state.textGroupUrns[text.urn.toString()],
          urn: text.urn.toString(),
        })),
      })),
    }));
  },
  sortedByURN(state, getters) {
    const tmp = [...getters.hydratedTextGroups];
    tmp.sort((a, b) => a.urn.localeCompare(b.urn));
    return tmp;
  },
  sortedByTextGroup(state, getters) {
    const tmp = [...getters.hydratedTextGroups];
    tmp.sort((a, b) => a.label.localeCompare(b.label));
    return tmp;
  },
  hydratedWorks(state) {
    return state.textGroupWorks.map(work => ({
      ...state.textGroupUrns[work.urn.toString()],
      urn: work.urn.toString(),
      textGroup: state.textGroupUrns[work.urn.upTo('textGroup')],
      texts: work.texts.map(text => ({
        ...state.textGroupUrns[text.urn.toString()],
        urn: text.urn.toString(),
      })),
    }));
  },
  sortedByWork(state, getters) {
    const tmp = [...getters.hydratedWorks];
    tmp.sort((a, b) => a.label.localeCompare(b.label));
    return tmp;
  },
};
