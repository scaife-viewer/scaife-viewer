<template>
  <div class="widget ancestors" v-if="passage.ancestors && passage.ancestors.length > 0">
    <h2>Ancestors</h2>
    <p>
      <a v-for="ancestor in passage.ancestors" :key="`pa-${ancestor.urn}`" href="#" @click.prevent="setRef(ancestor.reference)">{{ ancestor.reference }}</a>
    </p>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
    }),
  },
  methods: {
    ...mapActions(['setRef']),
  },
};
</script>
