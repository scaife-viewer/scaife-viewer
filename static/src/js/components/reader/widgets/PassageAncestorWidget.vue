<template>
  <div class="widget ancestors" v-if="passage.ancestors && passage.ancestors.length > 0">
    <h2>Ancestors</h2>
    <p>
      <router-link v-for="ancestor in passage.ancestors" :key="`pa-${ancestor.urn}`" :to="toRef(ancestor.reference)">{{ ancestor.reference }}</router-link>
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
