<template>
  <div class="widget selected-word" v-if="word">
    <h2>Selected Word</h2>
    <p>{{ word }}</p>
  </div>
</template>

<script>
import store from '../../store';

export default {
  store,
  computed: {
    word() {
      let word = null;
      const { selectedWord } = this.$store.state.reader;
      if (selectedWord) {
        word = selectedWord.word; // eslint-disable-line prefer-destructuring
      }
      return word;
    },
  },
};
</script>
