<template>
  <div class="version-list">
    <template v-if="loading">
      <div class="ball-pulse partial-loader">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </template>
    <div v-else-if="error" class="text-center"><b>Error</b>: {{ error }}</div>
    <div v-else>
      <h2>Versions</h2>
      <div class="card-deck">
        <div class="version-card" v-for="text in versions" :key="text.url">
          <div class="card-body">
            <p class="text-subtype">{{ text.kind }}</p>
            <h4 class="card-title"><a :href="text.url">{{ text.label }}</a></h4>
            <p class="card-text">{{ text.description }}</p>
          </div>
          <div class="card-footer">
            <a :href="text.first_passage.url"><icon name="book"></icon> Read ({{ text.human_lang }})</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import constants from '../constants';

export default {
  name: 'cts-version-list',
  created() {
    this.loading = true;
    this.$store.dispatch(constants.LIBRARY_LOAD_VERSION_LIST, this.$route.params.urn)
      .then(() => {
        this.loading = false;
      })
      .catch((err) => {
        this.loading = false;
        this.error = err.message;
        throw err;
      });
  },
  data() {
    return {
      loading: false,
      error: '',
    };
  },
  computed: {
    versions() {
      return this.$store.state.library.versions;
    }
  },
};
</script>
