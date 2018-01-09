<template>
  <widget class="selected-word" v-if="word">
    <span slot="header">Selected Word</span>
    <div slot="body">
      {{ word.w }}[{{ word.i }}]
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget';

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
  components: {
    widget,
  },
};
</script>
