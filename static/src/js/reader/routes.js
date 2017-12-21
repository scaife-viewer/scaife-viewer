import { URN } from '../scaife-viewer';
import Reader from './reader';

export default [
  {
    path: '/reader/:leftUrn',
    component: {
      components: {
        Reader,
      },
      computed: {
        leftUrn() {
          return new URN(this.$route.params.leftUrn);
        },
        rightUrn() {
          const { right } = this.$route.query;
          if (!right) {
            return null;
          }
          return this.leftUrn.replace({ version: right });
        },
      },
      template: '<reader :leftUrn="leftUrn" :rightUrn="rightUrn"></reader>',
    },
    name: 'reader',
  },
];
