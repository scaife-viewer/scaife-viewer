<template>
  <widget class="search">
    <span slot="header">
      Text Search
      <span v-if="query" class="result-count">({{ totalCount }})</span>
    </span>
    <div slot="sticky">
      <div class="search-input">
        <input v-model="query" type="text" class="form-control form-control-sm" />
      </div>
    </div>
    <div slot="body">
      <div class="search-hits">
        <ul>
          <li v-for="r in results" :key="r.passage.urn">
            <router-link :to="toPassage(r.passage.urn)" :class="{ active : r.active }">{{ r.passage.refs.start.human_reference }}</router-link>
          </li>
        </ul>
      </div>
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
    passage: 'doTextSearch',
    query: 'updateSearch',
    activeResults: 'updateHighlights',
  },
  created() {
    this.doTextSearch();
  },
  data() {
    return {
      query: this.$store.state.route.query.q,
      totalCount: 0,
      results: [],
    };
  },
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
    activeResults() {
      return this.results.filter(({ active }) => active);
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
      return new Promise((resolve, reject) => {
        if (!this.passage.ready) {
          resolve();
        } else {
          const params = {
            q: this.query.trim(),
            text: this.passage.urn.upTo('version'),
          };
          sv.textSearch(params)
            .then(({ total_count: totalCount, results }) => {
              this.totalCount = totalCount;
              this.results = results.map((result) => {
                const active = result.passage.urn === this.passage.urn.toString();
                return { ...result, active };
              });
            })
            .then(resolve)
            .catch(reject);
        }
      });
    },
    updateHighlights() {
      this.$store.commit('reader/clearAnnotation', { key: 'highlighted' });
      this.activeResults.forEach(({ highlights }) => {
        this.$store.commit('reader/setAnnotations', {
          tokens: highlights.map(({ w, i }) => `${w}[${i}]`),
          key: 'highlighted',
          value: true,
        });
      });
    },
  },
  components: {
    widget,
  },
};
</script>
