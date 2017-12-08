<template>
  <div class="widget">
    <h2>CTS URN</h2>
    <p>
      <tt><a :href="`https://perseus-cts.eu1.eldarioncloud.com/api/cts?request=GetPassage&amp;urn=${passage.urn}`">{{ passage.urn.toString() }}</a></tt>
    </p>
  </div>
</template>

<script>
import store from '../../store';

export default {
  store,
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
};
</script>
