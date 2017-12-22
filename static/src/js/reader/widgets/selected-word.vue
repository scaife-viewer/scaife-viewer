<template>
  <div class="widget" v-if="word">
    <h2>Selected Word</h2>
    {{ word }}
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
