'use strict';

var _ajax = require('./ajax');

var _ajax2 = _interopRequireDefault(_ajax);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

/* global window document */
window.jQuery = window.$ = require('jquery');

var $ = window.$;

window.Popper = require('popper.js');
require('bootstrap');

$(function () {
    $(document).ajaxSend(_ajax2.default);

    // Topbar active tab support
    $('.topbar li').removeClass('active');

    var classList = $('body').attr('class').split(/\s+/);
    $.each(classList, function (index, item) {
        var selector = 'ul.nav li#tab_' + item;
        $(selector).addClass('active');
    });

    $('#account_logout, .account_logout').click(function (e) {
        e.preventDefault();
        $('#accountLogOutForm').submit();
    });
});