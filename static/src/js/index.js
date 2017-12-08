/* global $ */

import Vue from 'vue';
import VueRouter from 'vue-router';
import vueCustomElement from 'vue-custom-element';
import CTSTextGroupList from '@/js/components/CTSTextGroupList';
import CTSWorkList from '@/js/components/CTSWorkList';
import CTSTocList from '@/js/components/CTSTocList';
import router from '@/js/router';
import ajaxSendMethod from '@/js/ajax';
import Popper from 'popper.js';
import 'document-register-element/build/document-register-element';
import '@/scss/index.scss';
import '@/images/perseus_running_man.png';
import '@/images/perseus_running_man_small.png';

// for the bootstrap
window.Popper = Popper;
require('bootstrap');

Vue.use(VueRouter);
Vue.use(vueCustomElement);

Vue.customElement('sv-cts-textgroup-list', CTSTextGroupList);
Vue.customElement('sv-cts-work-list', CTSWorkList);
Vue.customElement('sv-cts-toc-list', CTSTocList);
Vue.customElement('sv-reader', {
  router, // tied to sv-reader until we vueify the whole site
  template: '<router-view />',
});

$(() => {
  $(document).ajaxSend(ajaxSendMethod);

  // Topbar active tab support
  $('.topbar li').removeClass('active');

  const classList = $('body').attr('class').split(/\s+/);
  $.each(classList, (index, item) => {
    const selector = `ul.nav li#tab_${item}`;
    $(selector).addClass('active');
  });

  $('#account_logout, .account_logout').click((e) => {
    e.preventDefault();
    $('#accountLogOutForm').submit();
  });
});
