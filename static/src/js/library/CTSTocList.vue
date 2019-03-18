<template>
  <div class="toc-list">
    <page-loader v-if="loading" />
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
import constants from '../constants';

export default {
  name: 'cts-toc-list',
  created() {
    this.loading = true;
    this.$store.dispatch(constants.LIBRARY_LOAD_TOC_LIST, this.$route.params.urn)
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
      return this.$store.state.library.toc;
    },
  },
};
</script>
