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
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <div v-else>
      <ul>
        <li v-for="work in works" :key="work.url">
          <a :href="work.url"><b>{{ work.label }}</b></a>
          <ul>
            <li v-for="text in work.texts" :key="text.url">
              <b>{{ text.label }}</b>
              <p>
                <span class="text-muted">{{ text.description }}</span>
                <br><a :href="text.url">Read</a>
              </p>
            </li>
          </ul>
        </li>
      </ul>
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
