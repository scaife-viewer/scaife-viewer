<template>
  <base-widget>
    <span slot="header">Attributions</span>
    <div slot="body">
      <attributions-widget />
    </div>
  </base-widget>
</template>

<script>
import AttributionsWidget from '@scaife-viewer/widget-attributions';

export default {
  name: 'widget-attributions',
  components: {
    AttributionsWidget,
  },
};
</script>
