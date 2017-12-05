<template>
  <div class="widget children" v-if="passage.children && passage.children.length > 0">
    <h2>Children</h2>
    <p>
      <router-link v-for="child in passage.children" :key="`pc-${child.urn}`" :to="toRef(child.reference)">{{ child.lsb }}</router-link>
    </p>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { toRef } from '../utils';

export default {
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
    }),
  },
  methods: {
    toRef,
  },
};
</script>
