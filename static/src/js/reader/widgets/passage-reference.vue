<template>
  <widget class="passage-reference">
    <span slot="header">Passage Reference</span>
    <div slot="body">
      <input
        v-model="reference"
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
import widget from '../widget';
import ReaderNavigationMixin from '../reader-navigation-mixin';

export default {
  store,
  mixins: [
    ReaderNavigationMixin,
  ],
  watch: {
    passage: {
      handler: 'setInputRef',
      immediate: true,
    },
  },
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
  data() {
    return {
      reference: '',
    };
  },
  methods: {
    setInputRef() {
      this.reference = this.passage.urn.reference;
    },
    handleKeyUp(e) {
      if (e.keyCode === 13) {
        this.$router.push(this.toRef(this.reference));
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
