import VueRouter from 'vue-router';
import reader from './reader/routes';

const router = new VueRouter({
  mode: 'history',
  routes: [
    ...reader,
  ],
});

export default router;
