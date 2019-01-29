/* global $ */
import '@/scss/index.scss';
import '@/images/perseus_running_man.png';
import '@/images/perseus_running_man_small.png';

import loadApp from './app';

$(() => {
  loadApp();

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
