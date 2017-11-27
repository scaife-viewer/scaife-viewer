/* global $ */

import Vue from 'vue';
import vueCustomElement from 'vue-custom-element';
import CTSTextGroupList from '@/js/components/CTSTextGroupList';
import CTSWorkList from '@/js/components/CTSWorkList';
import CTSTocList from '@/js/components/CTSTocList';
import ajaxSendMethod from '@/js/ajax';
import Popper from 'popper.js';
import 'document-register-element/build/document-register-element';
import '@/scss/index.scss';
import '@/images/perseus_running_man.png';
import '@/images/perseus_running_man_small.png';

// for the bootstrap
window.Popper = Popper;
require('bootstrap');

Vue.use(vueCustomElement);

Vue.customElement('sv-cts-textgroup-list', CTSTextGroupList);
Vue.customElement('sv-cts-work-list', CTSWorkList);
Vue.customElement('sv-cts-toc-list', CTSTocList);

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
