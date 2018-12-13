<template>
  <span :class="[t, { c: clickable, selected, highlighted }]" @click.prevent="onClick">
  </span>
</template>
<script>
export default {
  name: 'token',
  props: {
    t: {
      type: String,
      required: true,
    },
    w: {
      type: String,
      required: true,
    },
    i: {
      type: String,
      required: true,
    },
  },
  inject: ['highlighting'],
  computed: {
    idx() {
      return `${this.w}[${this.i}]`;
    },
    textMode() {
      return this.$store.state.reader.textMode;
    },
    annotations() {
      return this.$store.state.reader.annotations;
    },
    annotation() {
      return this.annotations.get(this.idx);
    },
    clickable() {
      return this.$parent.visible && this.highlighting && this.textMode === 'clickable';
    },
    selected() {
      return this.annotation && this.annotation.selected;
    },
    highlighted() {
      return this.annotation && this.annotation.highlighted;
    }
  },
  methods: {
    readerDispatch(action, params) {
      this.$store.dispatch(`reader/${action}`, params);
    },
    onClick(e) {
      if (this.clickable) {
        if (e.metaKey) {
          if (this.selected) {
            this.readerDispatch(constants.READER_SET_SELECTED_TOKEN, { token: null });
          }
        } else if (e.shiftKey) {
          this.readerDispatch(constants.READER_SELECT_TOKEN_RANGE, { token: this.idx });
        } else {
          this.readerDispatch(constants.READER_SET_SELECTED_TOKEN, { token: this.idx });
        }
        e.stopPropagation();
      }
    }
  },
};
</script>
