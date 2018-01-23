<template>
  <widget class="search">
    <span slot="header">Text Search</span>
    <div slot="body">
      <input v-model="query" type="text" class="form-control form-control-sm" />
      <h3>{{ results.length }} results for "{{ query }}"</h3>
      <ul>
        <li v-for="r in results" :key="r.passage.urn">
          <router-link :to="toPassage(r.passage.urn)">{{ r.passage.refs.start.human_reference }} [{{ r.passage.text.lang }}]</router-link>
        </li>
      </ul>
    </div>
  </widget>
</template>

<script>
import sv from '../../scaife-viewer';
import store from '../../store';
import widget from '../widget';
import ReaderNavigationMixin from '../reader-navigation-mixin';

const debounce = require('lodash.debounce');

export default {
  store,
  mixins: [
    ReaderNavigationMixin,
  ],
  watch: {
    passage() {
      this.doTextSearch();
    },
    query() {
      this.updateSearch();
    },
  },
  created() {
    this.doTextSearch();
  },
  data() {
    return {
      query: this.$store.state.route.query.q,
      results: [],
    };
  },
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
  methods: {
    updateSearch: debounce(
      function f() {
        const query = this.query.trim();
        this.doTextSearch().then(() => {
          this.$router.push({
            name: 'reader',
            params: this.$store.state.route.params,
            query: { ...this.$store.state.route.query, q: query },
          });
        });
      },
      250,
    ),
    doTextSearch() {
      const params = {
        q: this.query.trim(),
        work: this.passage.urn.upTo('work'),
      };
      return sv.textSearch(params).then((results) => {
        this.results = results;
      });
    },
  },
  components: {
    widget,
  },
};
</script>
