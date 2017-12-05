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
import { mapState } from 'vuex';
import { toRef } from '../utils';

export default {
  created() {
    this.setInputRef();
  },
  data() {
    return {
      reference: '',
    };
  },
  watch: {
    passage: 'setInputRef',
  },
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
    }),
  },
  methods: {
    setInputRef() {
      const buf = [];
      buf.push(this.passage.refs.start.reference);
      if (this.passage.refs.end) {
        buf.push(`-${this.passage.refs.end.reference}`);
      }
      this.reference = buf.join('');
    },
    handleKeyUp(e) {
      if (e.keyCode === 13) {
        this.$router.push(toRef(this.reference));
      }
    },
    handleClick(e) {
      const el = e.currentTarget;
      el.select();
    },
  },
};
</script>
