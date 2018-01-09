<template>
  <div :class="['textpart']">
    <router-link v-if="reference" class="a" :to="toRef(this.reference)"><div>{{ n }}</div></router-link>
    <div class="b">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import ReaderNavigationMixin from './reader-navigation-mixin';

export default {
  name: 'TextPart',
  mixins: [
    ReaderNavigationMixin,
  ],
  props: {
    reference: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      visible: false,
    };
  },
  computed: {
    n() {
      return this.reference.split('.').pop();
    },
  },
};
</script>
