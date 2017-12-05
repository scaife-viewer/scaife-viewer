<template>
  <reader :urn="urn" :rightUrn="rightUrn"></reader>
</template>

<script>
import Reader from './Reader';
import parseURN from '../../urn';

export default {
  computed: {
    urn() {
      return this.$route.params.urn;
    },
    rightUrn() {
      const { right } = this.$route.query;
      if (!right) {
        return undefined;
      }
      const p = parseURN(this.urn);
      let urn = `urn:${p.urnNamespace}:${p.ctsNamespace}:${p.textGroup}.${p.work}.${right}`;
      if (p.reference) {
        urn += `:${p.reference}`;
      }
      return urn;
    },
  },
  components: {
    Reader,
  },
};
</script>
