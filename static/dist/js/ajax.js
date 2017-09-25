'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
/* global document */

var getCookie = function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

var sameOrigin = function sameOrigin(url) {
  // url could be relative or scheme relative or absolute
  var host = document.location.host; // host + port
  var protocol = document.location.protocol;
  var srOrigin = '//' + host;
  var origin = '' + protocol + srOrigin;

  // Allow absolute or scheme relative URLs to same origin
  return url == origin || url.slice(0, origin.length + 1) == origin + '/' || url == srOrigin || url.slice(0, srOrigin.length + 1) == srOrigin + '/' ||
  // or any other URL that isn't scheme relative or absolute i.e relative.
  !/^(\/\/|http:|https:).*/.test(url);
};

var safeMethod = function safeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
  );
};

var ajaxSendMethod = function ajaxSendMethod(event, xhr, settings) {
  if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
  }
};

exports.default = ajaxSendMethod;