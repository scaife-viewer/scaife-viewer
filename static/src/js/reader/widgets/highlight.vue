<template>
  <div class="widget highlight">
    <h2>Highlight</h2>
    <p>
      <input
        v-model="value"
        v-on:keyup="handleKeyUp"
        v-on:click="handleClick"
        type="text"
        class="form-control form-control-sm"
      >
    </p>
  </div>
</template>

<script>
import store from '../../store';

export default {
  store,
  watch: {
    highlight: 'setInputVal',
  },
  mounted() {
    this.setInputVal();
  },
  computed: {
    highlight() {
      return this.$store.state.reader.highlight;
    },
  },
  data() {
    return {
      value: '',
    };
  },
  methods: {
    setInputVal() {
      this.value = this.highlight;
    },
    handleKeyUp(e) {
      if (e.keyCode === 13) {
        this.$store.dispatch('reader/highlight', { highlight: this.value });
        e.currentTarget.blur();
      } else {
        e.stopPropagation();
      }
    },
    handleClick(e) {
      const el = e.currentTarget;
      el.select();
    },
  },
};
</script>
