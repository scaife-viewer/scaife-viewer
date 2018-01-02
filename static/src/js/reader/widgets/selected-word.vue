<template>
  <div class="widget selected-word" v-if="word">
    <h2>Selected Word</h2>
    <p>{{ word.w }}[{{ word.i }}]</p>
  </div>
</template>

<script>
import store from '../../store';

export default {
  store,
  computed: {
    word() {
      let word = null;
      const { highlight } = this.$store.state.reader;
      if (highlight) {
        const [, w, i] = /^@([^[]+)(?:\[(\d+)\])?$/.exec(highlight);
        word = { w, i };
      }
      return word;
    },
  },
};
</script>
