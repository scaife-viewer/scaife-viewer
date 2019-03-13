import createPersistedState from 'vuex-persistedstate';

import { library, reader } from './vuex';

const debug = process.env.NODE_ENV !== 'production';


export default function createStore() {
  return {
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
    strict: true,
    debug,
  };
}
