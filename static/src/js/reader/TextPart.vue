<template>
  <div class="textpart">
    <router-link v-if="reference" class="a" :to="toRef(this.reference)"><div>{{ n }}</div></router-link>
    <div class="b">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import ReaderNavigationMixin from '../mixins/ReaderNavigationMixin.vue';

export default {
  name: 'TextPart',
  mixins: [
    ReaderNavigationMixin,
  ],
  props: {
    reference: {
      type: String,
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
