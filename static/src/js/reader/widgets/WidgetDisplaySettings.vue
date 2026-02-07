<template>
  <base-widget>
    <span slot="header">Display Settings</span>
    <div slot="body">
      <h3>Text Size</h3>
      <text-size-widget />

      <h3>Text Width</h3>

      <text-width-widget />
    </div>
  </base-widget>
</template>

<script>
import { TextSizeWidget, TextWidthWidget } from "@scaife-viewer/scaife-widgets";
import WIDGETS_NS from "@scaife-viewer/scaife-widgets";

export default {
  name: "widget-display-settings",
  components: {
    TextSizeWidget,
    TextWidthWidget,
  },
  computed: {
    textSize() {
      return this.$store.state[WIDGETS_NS].readerTextSize;
    },
    textWidth() {
      return this.$store.state[WIDGETS_NS].readerTextWidth;
    },
  },
};
</script>

<style>
.subwidget-heading {
  margin-left: 22px;
}
</style>
