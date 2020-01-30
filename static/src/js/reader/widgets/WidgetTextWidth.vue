<template>
  <base-widget>
    <span slot="header">Text Width</span>
    <div slot="body">
      <text-width-widget />
    </div>
  </base-widget>
</template>

<script>
import constants from '../../constants';
import { TextWidthWidget } from '@scaife-viewer/scaife-widgets';
import WIDGETS_NS from '@scaife-viewer/scaife-widgets';

export default {
  name: 'widget-text-width',
  components: {
    TextWidthWidget,
  },
  computed: {
    textWidth() {
      return this.$store.state[WIDGETS_NS].readerTextWidth;
    },
  },
};
</script>
