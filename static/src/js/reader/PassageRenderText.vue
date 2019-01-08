<template>
  <div :class="['text', `text-${textSize}`]" @mousedown="handleMouseDown">
    <component
      :class="{'text-loading': text === null, 'text-loaded': text !== null}"
      :is="renderedText"
    />
  </div>
</template>

<script>
import constants from '../constants';
import TextPart from './TextPart.vue';
import InlineToken from './InlineToken.vue';
import RefLower from './RefLower.vue';

export default {
  name: 'passage-render-text',
  props: ['text', 'highlighting'],
  watch: {
    text: 'prepareText',
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
  provide() {
    return {
      highlighting: this.highlighting,
    };
  },
  created() {
    this.prepareText();
  },
  methods: {
    handleMouseDown(e) {
      if (this.highlighting && this.$store.state.reader.textMode === 'clickable') {
        e.preventDefault();
      }
    },
    prepareText() {
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
        this.$nextTick(this.renderText);
      }
    },
    renderText() {
      let observer = null;
      this.renderedText = {
        template: this.text,
        created() {
          const opts = {
            root: null,
            rootMargin: '0px',
            threshold: 0,
          };
          observer = new IntersectionObserver(this.ioCallback, opts);
        },
        mounted() {
          this.$nextTick(() => {
            this.$el.querySelectorAll('.textpart.o').forEach((e) => {
              observer.observe(e);
            });
          });
        },
        destroy() {
          observer.disconnect();
          observer = null;
        },
        methods: {
          ioCallback(entries) {
            entries.forEach((entry) => {
              if (entry) {
                const vm = entry.target.__vue__; // eslint-disable-line no-underscore-dangle
                if (vm) {
                  vm.visible = entry.isIntersecting;
                }
              }
            });
          },
        },
        components: {
          RefLower,
          TextPart,
          t: InlineToken,
        },
      };
    },
  },
};
</script>
