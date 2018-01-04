<template>
  <div class="widget children" v-if="passage.metadata.children && passage.metadata.children.length > 0">
    <h2>Children</h2>
    <p>
      <template v-for="(child, idx) in passage.metadata.children">
        <!-- unable to figure how to insert a breaking space with vue (uses css :after but is included in <a>) -->
        <router-link :key="`pc-${child.lsb}`" :to="toRef(child.reference)">{{ child.lsb }}</router-link>
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
