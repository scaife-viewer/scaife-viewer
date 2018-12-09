<template>
  <widget class="highlight">
    <span slot="header">Highlight</span>
    <div slot="body">
      <input
        v-model="value"
        v-on:keyup="handleKeyUp"
        v-on:click="handleClick"
        type="text"
        class="form-control form-control-sm"
      >
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget.vue';

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
        if (this.value === '') {
          this.$store.dispatch('reader/highlight', { highlight: null });
        } else {
          this.$store.dispatch('reader/highlight', { highlight: this.value });
        }
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
  components: {
    widget,
  },
};
</script>
