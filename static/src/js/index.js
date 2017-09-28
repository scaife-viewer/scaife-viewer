/* global window document */
window.jQuery = window.$ = require('jquery');

const $ = window.$;

window.Popper = require('popper.js');
require('bootstrap');

import Vue from 'vue';
import CTSResourceTable from './components/CTSResourceTable.vue';
import ajaxSendMethod from './ajax';

$(() => {
    $(document).ajaxSend(ajaxSendMethod);

    // Topbar active tab support
    $('.topbar li').removeClass('active');

    const classList = $('body').attr('class').split(/\s+/);
    $.each(classList, (index, item) => {
        const selector = `ul.nav li#tab_${item}`;
        $(selector).addClass('active');
    });

    $('#account_logout, .account_logout').click(e => {
        e.preventDefault();
        $('#accountLogOutForm').submit();
    });
});

if (document.querySelector('#resources')) {
  new Vue({
    el: '#resources',
    render(h) {
      return h(CTSResourceTable);
    },
  });
}
