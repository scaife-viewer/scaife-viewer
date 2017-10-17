/* eslint-disable import/first */

// crazy jQuery bindings
const jQuery = require('jquery'); // eslint-disable-line import/newline-after-import
window.jQuery = jQuery;
window.$ = jQuery;
const $ = jQuery;

import 'document-register-element/build/document-register-element';

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

  $('.text-size-control').click((e) => {
    const el = e.currentTarget;
    const textSize = $(el).data('size');
    $('.text').removeClass('text-xs text-sm text-md text-lg text-xl');
    $('.text').addClass(`text-${textSize}`);
    $('.text-size-control').removeClass('active');
    $(el).addClass('active');
    localStorage.setItem('text-size', textSize);
  });

  if (!localStorage['text-size']) {
    localStorage.setItem('text-size', 'md');
  }
  $('.text').addClass(`text-${localStorage.getItem('text-size')}`);
  $(`.text-size-control.text-${localStorage.getItem('text-size')}`).addClass('active');

  $(document).on('keyup', (e) => {
    if (e.key === 'ArrowLeft') {
      const url = $('#pg-left').attr('href');
      if (url) {
        window.location = url;
      }
    } else if (e.key === 'ArrowRight') {
      const url = $('#pg-right').attr('href');
      if (url) {
        window.location = url;
      }
    }
  });

  if (localStorage.getItem('left-sidebar-open') === 'true') {
    $('#left-sidebar').removeClass('collapsed');
    $('#left-sidebar-toggle').addClass('open');
  } else {
    $('#left-sidebar').addClass('collapsed');
    $('#left-sidebar-toggle').removeClass('open');
  }

  $('#left-sidebar-toggle').click(() => {
    if (localStorage.getItem('left-sidebar-open') === 'true') {
      $('#left-sidebar').addClass('collapsed');
      $('#left-sidebar-toggle').removeClass('open');
      localStorage.setItem('left-sidebar-open', 'false');
    } else {
      $('#left-sidebar').removeClass('collapsed');
      $('#left-sidebar-toggle').addClass('open');
      localStorage.setItem('left-sidebar-open', 'true');
    }
  });

  if (localStorage.getItem('right-sidebar-open') === 'true') {
    $('#right-sidebar').removeClass('collapsed');
    $('#right-sidebar-toggle').addClass('open');
  } else {
    $('#right-sidebar').addClass('collapsed');
    $('#right-sidebar-toggle').removeClass('open');
  }

  $('#right-sidebar-toggle').click(() => {
    if (localStorage.getItem('right-sidebar-open') === 'true') {
      $('#right-sidebar').addClass('collapsed');
      $('#right-sidebar-toggle').removeClass('open');
      localStorage.setItem('right-sidebar-open', 'false');
    } else {
      $('#right-sidebar').removeClass('collapsed');
      $('#right-sidebar-toggle').addClass('open');
      localStorage.setItem('right-sidebar-open', 'true');
    }
  });

  function rsplit(s, sep, maxsplit) {
    const split = s.split(sep);
    return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;
  }

  $('.textpart .a').click((e) => {
    const el = e.currentTarget;
    const urn = $(el).closest('.text').data('urn');
    const ref = $(el).data('ref');
    const fullUrn = `${urn}:${ref}`;
    const baseUrl = rsplit(document.location.pathname, '/', 2)[0];
    window.location.href = `${baseUrl}/${fullUrn}`;
  });
});
