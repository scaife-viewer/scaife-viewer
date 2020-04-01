import './directives';
import Vue from 'vue';
import VueVirtualScroller from 'vue-virtual-scroller';
import store from './store';
import router from './router';
import App from './App.vue';

import globalComponents from './components';
import GraphQLPlugin from './atlas/gql';

Vue.config.productionTip = false;

export default () => {
  if (document.getElementById('app')) {
    globalComponents.forEach(component => Vue.component(component.name, component));

    Vue.use(GraphQLPlugin);
    Vue.use(VueVirtualScroller);

    /* eslint-disable no-new */
    new Vue({
      el: '#app',
      render: h => h(App),
      store,
      router,
    });
  }
};
