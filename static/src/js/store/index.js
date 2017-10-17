import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';
import library from '@/js/store/library';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    library,
  },
  plugins: [
    createPersistedState({
      paths: ['a'],
      storage: window.localStorage,
    }),
  ],
});

export default store;
