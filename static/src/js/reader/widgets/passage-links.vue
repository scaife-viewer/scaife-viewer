<template>
  <widget>
    <span slot="header">CTS URN</span>
    <div slot="body">
      <tt><a :href="`https://perseus-cts.eu1.eldarioncloud.com/api/cts?request=GetPassage&amp;urn=${passage.urn}`">{{ passage.urn.toString() }}</a></tt>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget';

export default {
  store,
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
  components: {
    widget,
  },
};
</script>
