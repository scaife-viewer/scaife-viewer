import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';
import library from '@/js/store/library';
import reader from '@/js/reader/store';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    library,
    reader,
  },
  plugins: [
    createPersistedState({
      paths: [
        'reader.sidebarLeftOpened',
        'reader.sidebarRightOpened',
        'reader.textSize',
        'reader.textMode',
      ],
      storage: window.localStorage,
    }),
  ],
});

export default store;
