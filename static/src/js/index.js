/* eslint-disable import/first */

// crazy jQuery bindings
const jQuery = require('jquery'); // eslint-disable-line import/newline-after-import
window.jQuery = jQuery;
window.$ = jQuery;
const $ = jQuery;

const Vue = require('vue');
const vueCustomElement = require('vue-custom-element');
const CTSTextGroupList = require('./components/CTSTextGroupList.vue');
const CTSWorkList = require('./components/CTSWorkList.vue');
const ajaxSendMethod = require('./ajax');

Vue.use(vueCustomElement);

Vue.customElement('sv-cts-textgroup-list', CTSTextGroupList);
Vue.customElement('sv-cts-work-list', CTSWorkList);

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
