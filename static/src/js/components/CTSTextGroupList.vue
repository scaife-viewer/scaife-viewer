<template>
  <div>
    <div class="input-group">
      <input
        type="text"
        class="form-control"
        v-model="query"
        placeholder="Find a text group..."
      >
      <span class="input-group-addon" v-if="filtered">
        <i class="fa fa-times" @click="clearQuery"></i>
      </span>
    </div>
    <template v-if="loading">
      <i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>
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
    this.$store.dispatch('loadTextGroups', document.location.href).then(() => {
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
  computed: mapState(['textGroups']),
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
