<template>
  <div class="widget ancestors" v-if="passage.metadata.ancestors && passage.metadata.ancestors.length > 0">
    <h2>Ancestors</h2>
    <p>
      <template v-for="(ancestor, idx) in passage.metadata.ancestors">
        <router-link :key="`pa-${ancestor.reference}`" :to="toRef(ancestor.reference)">{{ ancestor.reference }}</router-link><template v-if="idx != passage.metadata.ancestors.length - 1">&gt; </template>
      </template>
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
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
};
</script>
