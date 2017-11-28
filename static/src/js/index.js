/* global $ */

import Vue from 'vue';
import vueCustomElement from 'vue-custom-element';
import CTSTextGroupList from '@/js/components/CTSTextGroupList';
import CTSWorkList from '@/js/components/CTSWorkList';
import CTSTocList from '@/js/components/CTSTocList';
import SinglePassageReader from '@/js/components/reader/SinglePassageReader';
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
Vue.customElement('sv-single-passage-reader', SinglePassageReader);

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

  function rsplit(s, sep, maxsplit) {
    const split = s.split(sep);
    return maxsplit ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit)) : split;
  }

  $('.textpart .a').click((e) => {
    const el = e.currentTarget;
    const urn = $('#overall').data('urn');
    const ref = $(el).data('ref');
    const fullUrn = `${urn}:${ref}`;
    const baseUrl = rsplit(document.location.pathname, '/', 2)[0];
    window.location.href = `${baseUrl}/${fullUrn}${window.location.search}`;
  });

  $('#passage-reference').keyup((e) => {
    if (e.keyCode === 13) {
      const el = e.currentTarget;
      const urn = $('#overall').data('urn');
      const ref = $(el).val();
      const fullUrn = `${urn}:${ref}`;
      const baseUrl = rsplit(document.location.pathname, '/', 2)[0];
      window.location.href = `${baseUrl}/${fullUrn}${window.location.search}`;
    } else {
      e.stopPropagation();
    }
  });

  $('#passage-reference').on('click', (e) => {
    const el = e.currentTarget;
    el.select();
  });
});
