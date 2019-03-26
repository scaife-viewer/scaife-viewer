<template>
  <base-widget class="ancestors" v-if="passage.metadata.ancestors && passage.metadata.ancestors.length > 0">
    <span slot="header">Ancestors</span>
    <div slot="body">
      <template v-for="(ancestor, idx) in passage.metadata.ancestors">
        <router-link :key="`pa-${ancestor.reference}`" :to="toRef(ancestor.reference)">{{ ancestor.reference }}</router-link><template v-if="idx != passage.metadata.ancestors.length - 1">&gt; </template>
      </template>
    </div>
  </base-widget>
</template>

<script>
import ReaderNavigationMixin from '../../mixins/ReaderNavigationMixin.vue';

export default {
  name: 'widget-passage-ancestors',
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
