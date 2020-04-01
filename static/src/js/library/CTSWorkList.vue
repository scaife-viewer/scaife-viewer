<template>
  <div class="work-list">
    <template v-if="loading">
      <div class="ball-pulse partial-loader">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </template>
    <div v-else-if="error" class="text-center"><b>Error</b>: {{ error }}</div>
    <div v-else>
      <h2>Works</h2>

      <div class="form-group">
        <div class="input-group">
          <input
            type="text"
            class="form-control"
            v-model="query"
            placeholder="Find a work..."
            ref="filter-input"
          >
          <div class="input-group-append" v-if="filtered">
            <button class="btn btn-outline-secondary" type="button" @click="clearQuery"><icon name="times"></icon></button>
          </div>
        </div>
      </div>
      <CTSWorkDeck
        v-for="work in filteredWorks"
        :key="work.urn"
        :work="work"
        :versions="versions"
      />
    </div>
  </div>
</template>

<script>

const debounce = require('lodash.debounce');
import gql from 'graphql-tag';
import constants from '../constants';

import CTSWorkDeck from './CTSWorkDeck.vue';

export default {
  components: { CTSWorkDeck },
  name: 'cts-work-list',
  // created() {
  //   // this.loading = true;
  //   this.$store.dispatch(constants.LIBRARY_LOAD_WORK_LIST, this.$route.params.urn)
  //     .then(() => {
  //       // this.loading = false;
  //       this.$nextTick(() => {
  //         this.$refs['filter-input'].focus();
  //       });
  //     })
  //     .catch((err) => {
  //       // this.loading = false;
  //       this.error = err.message;
  //       throw err;
  //     });
  // },
  mounted() {
    this.$nextTick(() => {
      const filterInput = this.$refs['filter-input'];
      if (filterInput) {
        filterInput.focus();
      }
    });
  },
  data() {
    return {
      // loading: false,
      error: '',
      query: '',
      trimmedQuery: '',
      filtered: false,
    };
  },
  watch: {
    query() {
      this.filter();
    },
    loading() {
      if (!this.loading) {
        this.$nextTick(() => {
          this.$refs['filter-input'].focus();
        });
      }
    },
  },
  computed: {
    loading() {
      return !this.gqlData;
    },
    urn() {
      return `${this.$route.params.urn}`;
    },
    works() {
      return this.gqlData
        ? this.gqlData.works.edges.map(work => work.node)
        : [];
    },
    versions() {
      return this.gqlData
        ? this.gqlData.versions.edges.map(version => version.node)
        : [];
    },
    gqlQuery() {
      return gql`
        {
          works (urn_Startswith:"${this.urn}") {
            edges{
              node {
                urn
                label
              }
            }
          }
          versions (urn_Startswith: "${this.urn}"){
            edges {
              node {
                urn
                label
                kind
                description
                humanLang
                access
              }
            }
          }
        }`;
    },
    filteredWorks() {
      return this.filtered ? this.works.filter(work => work.label.toLowerCase().indexOf(this.trimmedQuery.toLowerCase()) !== -1) : this.works;
    },
  },
  methods: {
    clearQuery() {
      this.query = '';
    },
    filter: debounce(
      function f() {
        this.trimmedQuery = this.query.trim();
        if (this.trimmedQuery === '') {
          this.filtered = false;
        } else {
          this.filtered = true;
        }
      },
      250,
    ),
  },
};
</script>
