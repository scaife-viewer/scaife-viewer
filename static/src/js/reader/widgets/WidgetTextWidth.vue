<template>
  <base-widget>
    <span slot="header">Text Width</span>
    <div slot="body">
      <span :class="['text-width-control', {active: textWidth == 'narrow'}]" @click="changetextWidth('narrow')">Narrow</span>
      <span :class="['text-width-control', {active: textWidth == 'normal'}]" @click="changetextWidth('normal')">Normal</span>
      <span :class="['text-width-control', {active: textWidth == 'wide'}]" @click="changetextWidth('wide')">Wide</span>
      <span :class="['text-width-control', {active: textWidth == 'full'}]" @click="changetextWidth('full')">Full</span>
    </div>
  </base-widget>
</template>

<script>
import constants from '../../constants';

export default {
  name: 'widget-text-width',
  computed: {
    textWidth() {
      return this.$store.state.reader.textWidth;
    },
  },
  methods: {
    changetextWidth(width) {
      this.$store.commit(`reader/${constants.SET_TEXT_WIDTH}`, { width });
    },
  },
};
</script>
