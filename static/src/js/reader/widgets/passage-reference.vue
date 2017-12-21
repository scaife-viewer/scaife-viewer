<template>
  <div class="widget passage-reference">
    <h2>Passage Reference</h2>
    <p>
      <input
        v-model="reference"
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
import ReaderNavigationMixin from '../reader-navigation-mixin';

export default {
  store,
  mixins: [
    ReaderNavigationMixin,
  ],
  watch: {
    passage: 'setInputRef',
  },
  created() {
    this.setInputRef();
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
};
</script>
