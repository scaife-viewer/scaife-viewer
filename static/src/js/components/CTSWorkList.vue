<template>
  <div class="work-list">
    <div class="form-group">
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          v-model="query"
          placeholder="Find a work..."
          ref="filter-input"
        >
        <span class="input-group-addon" v-if="filtered">
          <i class="fa fa-times" @click="clearQuery"></i>
        </span>
      </div>
    </div>
    <template v-if="loading">
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <div v-else>
      <div class="work" v-for="work in works" :key="work.url">
        <h2><a :href="work.url"><b>{{ work.label }}</b></a></h2>
        <div class="card-deck">
          <div class="version-card" v-for="text in work.texts" :key="text.url">
            <div class="card-body">
              <p class="text-subtype">{{ text.subtype }}</p>
              <h4 class="card-title"><a :href="text.browse_url">{{ text.label }}</a></h4>
              <p class="card-text">{{ text.description }}</p>
            </div>
            <div class="card-footer">
              <a :href="text.read_url"><i class="fa fa-book"></i> Read ({{ text.human_lang }})</a>
            </div>
          </div>
        </div>
      </div>
    </div>
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
