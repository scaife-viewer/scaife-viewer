<template>
  <div class="widget children" v-if="passage.children && passage.children.length > 0">
    <h2>Children</h2>
    <p>
      <a v-for="child in passage.children" :key="`pc-${child.urn}`" href="#" @click.prevent="setRef(child.reference)">{{ child.lsb }}</a>
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
