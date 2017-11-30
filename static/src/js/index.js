/* global $ */

import Vue from 'vue';
import vueCustomElement from 'vue-custom-element';
import CTSTextGroupList from '@/js/components/CTSTextGroupList';
import CTSWorkList from '@/js/components/CTSWorkList';
import CTSTocList from '@/js/components/CTSTocList';
import Reader from '@/js/components/reader/Reader';
import ajaxSendMethod from '@/js/ajax';
import Popper from 'popper.js';
import 'document-register-element/build/document-register-element';
import '@/scss/index.scss';
import '@/images/perseus_running_man.png';

// for the bootstrap
window.Popper = Popper;
require('bootstrap');

Vue.use(vueCustomElement);

Vue.customElement('sv-cts-textgroup-list', CTSTextGroupList);
Vue.customElement('sv-cts-work-list', CTSWorkList);
Vue.customElement('sv-cts-toc-list', CTSTocList);
Vue.customElement('sv-reader', Reader);

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
