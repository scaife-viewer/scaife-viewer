import VueRouter from 'vue-router';
import { sync } from 'vuex-router-sync';
import store from './store';
import reader from './reader/routes';

const router = new VueRouter({
  mode: 'history',
  routes: [
    ...reader,
  ],
});

sync(store, router);

export default router;
