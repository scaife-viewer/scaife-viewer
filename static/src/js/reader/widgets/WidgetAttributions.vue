<template>
  <base-widget>
    <span slot="header">Attributions</span>
    <div slot="body">
      <attributions-widget />
    </div>
  </base-widget>
</template>

<script>
import AttributionsWidget from './AttributionsWidget.vue';

export default {
  name: 'widget-attributions',
  components: {
    AttributionsWidget,
  },
};
</script>
