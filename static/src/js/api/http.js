import axios from 'axios';

const HTTP = axios.create({
  baseURL: '/',
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
});

export default HTTP;
