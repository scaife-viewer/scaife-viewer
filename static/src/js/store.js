import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';

import { library, reader } from './vuex';

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== 'production';

export default new Vuex.Store({
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
        'reader.textWidth',
      ],
      storage: window.localStorage,
    }),
  ],
  strict: true,
  debug,
});
