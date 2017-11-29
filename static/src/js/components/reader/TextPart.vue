<template>
  <div :class="['textpart']">
    <div v-if="reference" class="a" @click="setRef"><div>{{ n }}</div></div>
    <div class="b">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import store from '../../store';

export default {
  name: 'text-part',
  store,
  props: ['reference'],
  computed: {
    n() {
      return this.reference.split('.').pop();
    },
  },
  methods: {
    setRef() {
      this.$store.dispatch('setRef', this.reference);
    },
  },
};
</script>
