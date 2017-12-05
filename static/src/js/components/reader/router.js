import VueRouter from 'vue-router';
import ReaderRouter from './ReaderRouter';

export default new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/reader/:urn',
      component: ReaderRouter,
      name: 'reader',
    },
  ],
});
