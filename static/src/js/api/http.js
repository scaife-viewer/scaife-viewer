import axios from 'axios';

const HTTP = axios.create({
  baseURL: '/api/v1/',
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
});

export default HTTP;
