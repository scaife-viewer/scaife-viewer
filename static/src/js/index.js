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
const CTSVersionList = require('./components/CTSVersionList.vue');
const ajaxSendMethod = require('./ajax');

Vue.use(vueCustomElement);

Vue.customElement('sv-cts-textgroup-list', CTSTextGroupList);
Vue.customElement('sv-cts-work-list', CTSWorkList);
Vue.customElement('sv-cts-version-list', CTSVersionList);

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

  $('.text-size-control').click(() => {
    const textSize = $(this).data('size');
    $(this).closest('.text').removeClass('text-xs text-sm text-md text-lg text-xl');
    $(this).closest('.text').addClass(`text-${textSize}`);
    localStorage.setItem('text-size', textSize);
  });

  if (!localStorage['text-size']) {
    localStorage.setItem('text-size', 'md');
  }
  $('.text').addClass(`text-${localStorage.getItem('text-size')}`);
});
