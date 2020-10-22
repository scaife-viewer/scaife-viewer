import URN from '@scaife-viewer/common';
import { MODULE_NS } from '@scaife-viewer/store';

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

const createStoreShim = () => ({
  namespace: MODULE_NS,
  store: {
    namespaced: true,
    state: {},
    getters: {
      passage: passageGetter,
    },
    actions: {},
    mutations: {},
  },
});

export default createStoreShim;
