import createPersistedState from 'vuex-persistedstate';
import { scaifeWidgets } from '@scaife-viewer/scaife-widgets';

import { library, reader } from './vuex';

const debug = process.env.NODE_ENV !== 'production';


export default function createStore() {
  return {
    modules: {
      library,
      reader,
      [scaifeWidgets.namespace]: scaifeWidgets.store,
    },
    plugins: [
      createPersistedState({
        paths: [
          'reader.sidebarLeftOpened',
          'reader.sidebarRightOpened',
          'reader.textMode',
        ],
        storage: window.localStorage,
      }),
    ],
    strict: true,
    debug,
  };
}
