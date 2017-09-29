<template>
  <div>
    <div class="form-group">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          v-model="query"
          placeholder="Find a work..."
        >
        <span class="input-group-addon" v-if="filtered">
          <i class="fa fa-times" @click="clearQuery"></i>
        </span>
      </div>
    </div>
    <template v-if="loading">
      <i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>
    </template>
    <table v-else class="table">
      <tr v-for="work in works" :key="work.url">
        <td><a :href="work.url">{{ work.label }}</a></td>
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
    this.$store.dispatch('loadWorks', document.location.href).then(() => {
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
  computed: mapState(['works']),
  methods: {
    clearQuery() {
      this.query = '';
    },
    filter: debounce(
      function f() {
        const query = this.query.trim();
        if (query === '') {
          this.$store.dispatch('resetWorks');
          this.filtered = false;
        } else {
          this.$store.dispatch('filterWorks', query);
          this.filtered = true;
        }
      },
      250,
    ),
  },
};
</script>
