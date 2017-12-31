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
      const { selectedWord } = this.$store.state.reader;
      if (selectedWord) {
        const { w: aw, i: ai } = this.$store.state.reader.selectedWord;
        const { w: bw, i: bi } = this;
        return aw === bw && ai === bi;
      }
      return false;
    },
  },
  methods: {
    handleClick(e) {
      if (this.t === 'w') {
        const word = { w: this.w, i: this.i };
        this.$store.dispatch('reader/selectWord', { word });
        const passage = this.$store.getters['reader/passage'];
        this.$router.push({
          name: 'reader',
          params: {
            leftUrn: passage.urn.toString(),
          },
          query: {
            ...this.$store.state.route.query,
            highlight: `@${this.w}[${this.i}]`,
          },
        });
      }
      e.stopPropagation();
    },
    handleMetaClick(e) {
      if (this.selected) {
        this.$store.dispatch('reader/selectWord', { word: null });
        const passage = this.$store.getters['reader/passage'];
        const { query } = this.$store.state.route;
        this.$router.push({
          name: 'reader',
          params: {
            leftUrn: passage.urn.toString(),
          },
          query: (({ highlight: deleted, ...o }) => o)(query),
        });
      }
      e.stopPropagation();
    },
  },
};
</script>
