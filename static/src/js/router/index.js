import Vue from 'vue';
import Router from 'vue-router';

import routes from './routes';

Vue.use(Router);

let base = process.env.FORCE_SCRIPT_NAME || '/';

// From vue-router docs:
// The base URL of the app. For example, if the entire single page application
// is served under /app/, then base should use the value "/app/".
if (base) {
  if (!base.startsWith('/')) {
    base = `/${base}`;
  }
  if (!base.endsWith('/')) {
    base = `${base}/`;
  }
}

const router = new Router({
  mode: 'history',
  base,
  routes,
});

export default router;
