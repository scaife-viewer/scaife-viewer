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
        this.$store.dispatch('reader/selectWord', { word: this.w, toggle: this.toggle });
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
