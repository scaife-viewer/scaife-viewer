/* global $ */

import Vue from 'vue';
import VueRouter from 'vue-router';
import { sync } from 'vuex-router-sync';
import vueCustomElement from 'vue-custom-element';
import Library from './components/Library';
import CTSWorkList from './components/CTSWorkList';
import CTSTocList from './components/CTSTocList';
import router from './router';
import store from './store';

sync(store, router);

Vue.use(VueRouter);
Vue.use(vueCustomElement);

Vue.directive('tooltip', (el, binding) => {
  $(el).tooltip({
    title: binding.value,
    placement: binding.arg,
    trigger: 'hover',
  });
});

Vue.directive('popover', (el, binding) => {
  $(el).popover({
    placement: binding.arg,
    ...binding.value,
  });
});

Vue.customElement('sv-library', Library);
Vue.customElement('sv-cts-work-list', CTSWorkList);
Vue.customElement('sv-cts-toc-list', CTSTocList);
Vue.customElement('sv-reader', {
  router, // tied to sv-reader until we vueify the whole site
  template: '<router-view />',
});
