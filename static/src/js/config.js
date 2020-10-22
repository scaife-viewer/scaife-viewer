import createPersistedState from 'vuex-persistedstate';
import { scaifeWidgets } from '@scaife-viewer/scaife-widgets';
import { MODULE_NS as SHIM_MODULE_NS } from '@scaife-viewer/store';

import createStoreShim from './v2/store';


import { library, reader } from './vuex';

const debug = process.env.NODE_ENV !== 'production';

const scaifeStoreShim = createStoreShim();

export default function createStore() {
  return {
    modules: {
      library,
      reader,
      [scaifeWidgets.namespace]: scaifeWidgets.store,
      [SHIM_MODULE_NS]: scaifeStoreShim.store,
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
