<template>
  <div :class="['textpart']">
    <router-link v-if="reference" class="a" :to="toRef(this.reference)"><div>{{ n }}</div></router-link>
    <div class="b">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import store from '../../store';
import { toRef } from './utils';

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
    toRef,
  },
};
</script>
