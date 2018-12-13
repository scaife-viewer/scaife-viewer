<template>
  <base-widget class="selected-word" v-if="words && words.length > 0">
    <span slot="header">Selected Word</span>
    <div slot="body">
      <p v-for="word in words" :key="`${word.w}[${word.i}]`">{{ word.w }}[{{ word.i }}]</p>
    </div>
  </base-widget>
</template>

<script>
export default {
  name: 'widget-selected-word',
  computed: {
    words() {
      const words = [];
      const { annotations, annotationChange } = this.$store.state.reader;
      annotations.forEach((o, token) => {
        if (o.selected) {
          const [, w, i] = /^([^[]+)(?:\[(\d+)\])?$/.exec(token);
          words.push({ w, i });
        }
      });
      return words;
    },
  },
};
</script>
