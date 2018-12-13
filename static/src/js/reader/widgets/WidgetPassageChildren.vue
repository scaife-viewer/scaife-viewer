<template>
  <base-widget class="children" v-if="passage.metadata.children && passage.metadata.children.length > 0">
    <span slot="header">Children</span>
    <div slot="body">
      <template v-for="(child, idx) in passage.metadata.children">
        <!-- unable to figure how to insert a breaking space with vue (uses css :after but is included in <a>) -->
        <router-link :key="`pc-${child.lsb}`" :to="toRef(child.reference)">{{ child.lsb }}</router-link>
      </template>
    </div>
  </base-widget>
</template>

<script>
import ReaderNavigationMixin from '../../mixins/ReaderNavigationMixin.vue';

export default {
  name: 'widget-passage-children',
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
