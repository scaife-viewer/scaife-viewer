import './directives';
import Vue from 'vue';

import store from './store';
import router from './router';
import App from './App.vue';

import globalComponents from './components';

Vue.config.productionTip = false;

export default () => {
  if (document.getElementById('app')) {
    Vue.component('Icon', (resolve) => {
      require(['./components/Icon.vue'], resolve);
    });
    globalComponents.forEach(component => Vue.component(component.name, component));

    /* eslint-disable no-new */
    new Vue({
      el: '#app',
      render: h => h(App),
      store,
      router,
    });
  }
};
