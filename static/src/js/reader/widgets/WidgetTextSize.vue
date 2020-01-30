<template>
  <base-widget>
    <span slot="header">Text Size</span>
    <div slot="body">
      <text-size-widget />
    </div>
  </base-widget>
</template>

<script>
import constants from '../../constants';
import { TextSizeWidget } from '@scaife-viewer/scaife-widgets';
import WIDGETS_NS from '@scaife-viewer/scaife-widgets';

export default {
  name: 'widget-text-size',
  components: {
    TextSizeWidget,
  },
  computed: {
    textSize() {
      return this.$store.state[WIDGETS_NS].readerTextSize;
    },
  },
};
</script>
