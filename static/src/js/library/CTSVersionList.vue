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
        <div class="version-card" v-for="text in versions" :key="text.urn">
          <div class="card-body">
            <p class="text-subtype">{{ text.kind }}</p>
            <h4 class="card-title"><a :href="getLibraryURL(text)">{{ text.label }}</a></h4>
            <p class="card-text">{{ text.description }}</p>
          </div>
          <div class="card-footer">
            <a :href="getReaderURL(text)"><icon name="book"></icon> Read ({{ text.humanLang }})</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag';
// import constants from '../constants';

export default {
  name: 'cts-version-list',
  created() {
    // @@@ add loading / error handling to GraphQLPlugin
    // this.loading = true;
    // this.$store.dispatch(constants.LIBRARY_LOAD_VERSION_LIST, this.$route.params.urn)
    //   .then(() => {
    //     this.loading = false;
    //   })
    //   .catch((err) => {
    //     this.loading = false;
    //     this.error = err.message;
    //     throw err;
    //   });
  },
  data() {
    return {
      // loading: false,
      error: '',
    };
  },
  methods: {
    getLibraryURL(version) {
      return `/library/${this.safeURN(version.urn)}/`;
    },
    getReaderURL(version) {
      // @@@ prefer firstPassageUrl
      return `/library/${this.safeURN(version.urn)}/redirect/`;
    },
    safeURN(urn) {
      // @@@ maintain backwards compatability
      return urn.endsWith(':') ? urn.slice(0, -1) : urn;
    },
  },
  computed: {
    loading() {
      return !this.gqlData;
    },
    urn() {
      return `${this.$route.params.urn}`;
    },
    versions() {
      return this.gqlData
        ? this.gqlData.versions.edges.map(version => version.node)
        : [];
    },
    gqlQuery() {
      return gql`
        {
          versions (urn_Startswith:"${this.urn}") {
            edges{
              node {
                urn
                description
                kind
                label
                humanLang
                access
              }
            }
          }
        }`;
    },
  },
};
</script>
