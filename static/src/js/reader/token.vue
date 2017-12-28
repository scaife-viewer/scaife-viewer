<template>
  <span :class="[t, { selected }]" @click="handleClick" @click.meta="handleMetaClick"><slot></slot></span>
</template>

<script>
export default {
  name: 'Token',
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
  data() {
    return {
      selected: false,
    };
  },
  methods: {
    toggle() {
      this.selected = !this.selected;
    },
    handleClick(e) {
      if (this.t === 'w') {
        const word = { t: this.t, w: this.w, i: this.i };
        this.$store.dispatch('reader/selectWord', { word, toggle: this.toggle });
      }
      e.stopPropagation();
    },
    handleMetaClick(e) {
      if (this.selected) {
        this.$store.dispatch('reader/selectWord', { word: null, toggle: this.toggle });
      }
      e.stopPropagation();
    },
  },
};
</script>
