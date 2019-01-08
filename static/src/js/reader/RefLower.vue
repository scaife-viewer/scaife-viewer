<template>
  <span><router-link class="ref-lower" :to="toPassage(urn)"><span><slot></slot></span></router-link></span>
</template>

<script>
import ReaderNavigationMixin from './reader-navigation-mixin.vue';

export default {
  name: 'RefLower',
  mixins: [
    ReaderNavigationMixin,
  ],
  props: {
    urn: {
      type: String,
    },
  },
};
</script>
