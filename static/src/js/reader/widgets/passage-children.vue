<template>
  <widget class="children" v-if="passage.metadata.children && passage.metadata.children.length > 0">
    <span slot="header">Children</span>
    <div slot="body">
      <template v-for="(child, idx) in passage.metadata.children">
        <!-- unable to figure how to insert a breaking space with vue (uses css :after but is included in <a>) -->
        <router-link :key="`pc-${child.lsb}`" :to="toRef(child.reference)">{{ child.lsb }}</router-link>
      </template>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget.vue';

import ReaderNavigationMixin from '../reader-navigation-mixin.vue';

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
  components: {
    widget,
  },
};
</script>
