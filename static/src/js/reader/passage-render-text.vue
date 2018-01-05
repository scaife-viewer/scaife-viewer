<template>
  <div :class="['text', `text-${textSize}`]">
    <component :class="{'text-loading': text === null, 'text-loaded': text !== null}" :is="renderedText" />
  </div>
</template>

<script>
import store from '../store';
import TextPart from './text-part';
import TextLoader from './text-loader';
import Token from './token';

export default {
  store,
  props: ['text'],
  watch: {
    text: 'renderText',
  },
  data() {
    return {
      renderedText: null,
    };
  },
  computed: {
    textSize() {
      return this.$store.state.reader.textSize;
    },
  },
  created() {
    this.renderText();
  },
  methods: {
    renderText() {
      if (this.text === null) {
        // give the text fade out animation time to complete before
        // we show the loader.
        const delay = 250;
        setTimeout(() => {
          // check text before setting loader because it may have been
          // loaded faster than our delay.
          if (this.text === null) {
            this.renderedText = TextLoader;
          }
        }, delay);
      } else {
        this.renderedText = {
          store,
          template: this.text,
          components: {
            TextPart,
            t: Token,
          },
        };
      }
    },
  },
};
</script>
