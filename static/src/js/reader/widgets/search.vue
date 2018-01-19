<template>
  <widget class="search" v-if="query">
    <span slot="header">Text Search</span>
    <div slot="body">
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

export default {
  store,
  mixins: [
    ReaderNavigationMixin,
  ],
  watch: {
    passage() {
      this.doTextSearch();
    },
  },
  created() {
    this.doTextSearch();
  },
  data() {
    return {
      results: [],
    };
  },
  computed: {
    query() {
      return this.$store.state.route.query.q;
    },
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
  methods: {
    doTextSearch() {
      const params = {
        q: this.query,
        work: this.passage.urn.upTo('work'),
      };
      sv.textSearch(params).then((results) => {
        this.results = results.filter((result) => {
          return result.passage.urn !== this.passage.urn.toString();
        });
      });
    },
  },
  components: {
    widget,
  },
};
</script>
