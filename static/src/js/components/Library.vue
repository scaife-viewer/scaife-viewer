<template>
  <div>
    <div class="form-group">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          v-model="query"
          placeholder="Find a text group or work..."
          ref="filter-input"
        >
        <span class="input-group-addon" v-if="filtered">
          <i class="fa fa-times" @click="clearQuery"></i>
        </span>
      </div>
    </div>
    <div>
      <span @click="expandAll">expand all</span> | <span @click="collapseAll">collapse all</span>
    </div>
    <template v-if="loading">
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <template v-else v-for="textGroup in textGroups">
      <keep-alive>
        <library-text-group ref="collapsible" :textGroup="textGroup" :filtered="filtered" :key="textGroup.urn" />
      </keep-alive>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../store';
import LibraryTextGroup from './LibraryTextGroup';

const debounce = require('lodash.debounce');

export default {
  store,
  created() {
    this.loading = true;
    this.$store.dispatch('loadTextGroupList').then(() => {
      this.$refs['filter-input'].focus();
      this.loading = false;
    });
  },
  data() {
    return {
      loading: false,
      query: '',
      filtered: false,
    };
  },
  watch: {
    query() {
      this.filter();
    },
  },
  computed: {
    ...mapState({
      textGroups: state => state.library.textGroups,
    }),
  },
  methods: {
    clearQuery() {
      this.query = '';
    },
    filter: debounce(
      function f() {
        const query = this.query.trim();
        if (query === '') {
          this.$store.dispatch('resetTextGroups');
          this.filtered = false;
        } else {
          this.$store.dispatch('filterTextGroups', query);
          this.filtered = true;
        }
      },
      250,
    ),
    collapseAll() {
      this.$refs.collapsible.forEach((c) => {
        c.open = false;
      });
    },
    expandAll() {
      this.$refs.collapsible.forEach((c) => {
        c.open = true;
      });
    },
  },
  components: {
    LibraryTextGroup,
  },
};
</script>
