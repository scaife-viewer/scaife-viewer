/* global $ */

import ajaxSendMethod from '@/js/ajax';
import Popper from 'popper.js';
import 'document-register-element/build/document-register-element';
import '@/js/app';
import '@/scss/index.scss';
import '@/images/perseus_running_man.png';
import '@/images/perseus_running_man_small.png';

// for the bootstrap
window.Popper = Popper;
require('bootstrap');

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
