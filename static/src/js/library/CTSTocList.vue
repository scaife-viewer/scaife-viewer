<template>
  <div class="toc-list">
    <template v-if="loading">
      <div class="ball-grid-pulse page-loader">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </template>
    <div v-else-if="error" class="text-center"><b>Error</b>: {{ error }}</div>
    <div v-else>
      <h2>Table of Contents</h2>
      <div v-for="entry in toc" :key="entry.urn">
        <h3><a :href="entry.url">{{ entry.label }} {{ entry.num }}</a></h3>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  created() {
    this.loading = true;
    this.$store.dispatch('loadTocList', `/library/${this.$route.params.urn}/json/`)
      .then(() => {
        this.loading = false;
      })
      .catch((err) => {
        this.loading = false;
        this.error = err.message;
      });
  },
  data() {
    return {
      loading: false,
      error: '',
    };
  },
  computed: {
    toc() {
      return this.$stor.state.library.toc;
    },
  },
};
</script>
