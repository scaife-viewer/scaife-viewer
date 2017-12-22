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
      return this.$store.state.reader.selectedWord;
    },
  },
};
</script>
