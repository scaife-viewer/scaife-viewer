import VueRouter from 'vue-router';
import { sync } from 'vuex-router-sync';
import ReaderRouter from './ReaderRouter';
import store from '../../store';

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/reader/:urn',
      component: ReaderRouter,
      name: 'reader',
    },
  ],
});

sync(store, router);

export default router;
