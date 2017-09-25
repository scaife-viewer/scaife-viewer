/* global document */

const getCookie = name => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == `${name}=`) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
};

const sameOrigin = url => {
  // url could be relative or scheme relative or absolute
  const host = document.location.host; // host + port
  const protocol = document.location.protocol;
  const srOrigin = `//${host}`;
  const origin = `${protocol}${srOrigin}`;

  // Allow absolute or scheme relative URLs to same origin
  return (url == origin || url.slice(0, origin.length + 1) == `${origin}/`) ||
      (url == srOrigin || url.slice(0, srOrigin.length + 1) == `${srOrigin}/`) ||
      // or any other URL that isn't scheme relative or absolute i.e relative.
      !(/^(\/\/|http:|https:).*/.test(url));
};

const safeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);


const ajaxSendMethod = (event, xhr, settings) => {
  if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
  }
};

export default ajaxSendMethod;
