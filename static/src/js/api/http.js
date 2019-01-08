import axios from 'axios';

const baseURL = process.env.FORCE_SCRIPT_NAME || '/';

const HTTP = axios.create({
  baseURL,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
});

export default HTTP;
