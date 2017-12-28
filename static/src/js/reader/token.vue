<template>
  <span :class="[t, { selected }]" @click="handleClick"><slot></slot></span>
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
  },
};
</script>
