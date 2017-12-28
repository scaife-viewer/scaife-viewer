<template>
  <div :class="['text', `text-${textSize}`]">
    <text-loader v-if="!passage.ready" />
    <component v-if="passage.metadata" :class="{'text-loading': !passage.ready, 'text-loaded': passage.ready}" :is="renderedText"></component>
  </div>
</template>

<script>
import store from '../store';
import TextPart from './text-part';
import TextLoader from './text-loader';
import Token from './token';

export default {
  store,
  props: ['passage'],
  computed: {
    textSize() {
      return this.$store.state.reader.textSize;
    },
    renderedText() {
      return {
        store,
        template: this.passage.metadata.text_html,
        components: {
          TextPart,
          t: Token,
        },
      };
    },
  },
  components: {
    TextLoader,
  },
};
</script>
