import URN from '@scaife-viewer/common';
import createDefaultSVStore, { MODULE_NS } from '@scaife-viewer/store';

const passageGetter = function passageGetter(state, getters, rootState, rootGetters) {
  /*
  Mimics the passage getter from @scaife-viewer/store
  */
  const passage = rootGetters['reader/passage'];
  if (passage) {
    return new URN(passage.urn.value);
  }
  return null;
};

// eslint-disable-next-line arrow-body-style
const selectedLemmasGetter = (state, getters, rootState) => {
  /*
  Mimics the selectedLemmas getter from @scaife-viewer/store
  */
  return rootState.reader.selectedLemmas;
};

const createStoreShim = function createStoreShim() {
  const defaultStore = createDefaultSVStore().store;
  return {
    namespace: MODULE_NS,
    store: {
      namespaced: true,
      state: {
        ...defaultStore.state(),
      },
      getters: {
        ...defaultStore.getters,
        passage: passageGetter,
        selectedLemmas: selectedLemmasGetter,
      },
      actions: {
        ...defaultStore.actions,
      },
      mutations: {
        ...defaultStore.mutations,
      },
    },
  };
};
export default createStoreShim;
