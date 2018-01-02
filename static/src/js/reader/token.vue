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
  computed: {
    selected() {
      const { highlight } = this.$store.state.reader;
      if (highlight) {
        const [, aw, ai] = /^@([^[]+)(?:\[(\d+)\])?$/.exec(highlight);
        const { w: bw, i: bi } = this;
        return aw === bw && ai === bi;
      }
      return false;
    },
  },
  methods: {
    handleClick(e) {
      if (this.t === 'w') {
        this.$store.dispatch('reader/highlight', { highlight: `@${this.w}[${this.i}]` });
      }
      e.stopPropagation();
    },
    handleMetaClick(e) {
      if (this.selected) {
        this.$store.dispatch('reader/highlight', { highlight: null });
      }
      e.stopPropagation();
    },
  },
};
</script>
