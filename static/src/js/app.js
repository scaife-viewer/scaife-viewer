import './directives';
import Vue from 'vue';
import VueApollo from 'vue-apollo';

import store from './store';
import router from './router';
import apolloProvider from './v2/gql';
import App from './App.vue';
import { SkeletonPlugin } from '@scaife-viewer/skeleton';
import { iconMap as commonIconMap } from '@scaife-viewer/common';
import { iconMap as deIconMap } from '@scaife-viewer/widget-dictionary-entries';

import globalComponents from './components';

Vue.config.productionTip = false;

export default () => {
  if (document.getElementById('app')) {
    globalComponents.forEach(component => Vue.component(component.name, component));

    Vue.use(VueApollo);
    Vue.use(SkeletonPlugin, {
      iconMap: {
        ...commonIconMap,
        ...deIconMap,
      },
      config: {
        dictionaryEntries: {
          showCitationResolutionHint: false,
          resolveUsingNormalizedLemmas: true,
          selectDictionaries: false,
        },
      },
    });

    /* eslint-disable no-new */
    new Vue({
      el: '#app',
      render: h => h(App),
      store,
      router,
      apolloProvider,
    });
  }
};
