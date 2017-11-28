<template>
  <div class="widget">
    <h2>Text Size</h2>
    <p>
      <span class="text-size-control text-xs" @click="changeTextSize('xs')">Αα</span>
      <span class="text-size-control text-sm" @click="changeTextSize('sm')">Αα</span>
      <span class="text-size-control text-md" @click="changeTextSize('md')">Αα</span>
      <span class="text-size-control text-lg" @click="changeTextSize('lg')">Αα</span>
      <span class="text-size-control text-xl" @click="changeTextSize('xl')">Αα</span>
    </p>
  </div>
</template>

<script>
import store from '../../../store';

export default {
  store,
  methods: {
    changeTextSize(size) {
      this.$store.commit('setTextSize', size);
    },
  },
};
</script>
