<template>
  <div>
    <div class="form-group">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          v-model="query"
          placeholder="Find a text group..."
          ref="filter-input"
        >
        <span class="input-group-addon" v-if="filtered">
          <i class="fa fa-times" @click="clearQuery"></i>
        </span>
      </div>
    </div>
    <template v-if="loading">
      <div class="ball-pulse partial-loader">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </template>
    <table v-else class="table">
      <tr v-for="textGroup in textGroups" :key="textGroup.url">
        <td><a :href="textGroup.url">{{ textGroup.label }}</a></td>
      </tr>
    </table>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../store';

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
  },
};
</script>
