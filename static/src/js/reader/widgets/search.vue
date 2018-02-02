<template>
  <widget class="search">
    <span slot="header">
      Text Search
      <span v-if="query && totalCount" class="result-count">({{ totalCount }})</span>
    </span>
    <div slot="sticky">
      <div class="search-input">
        <input v-model="query" type="text" class="form-control form-control-sm" />
      </div>
    </div>
    <div slot="body" ref="body">
      <div class="search-hits">
        <div v-if="loading">loading</div>
        <ul v-else ref="items">
          <template v-for="(r, idx) in results">
            <li :class="{ first: idx === 0, last: isLast(idx) }" :key="r.passage.urn">
              <router-link :to="toPassage(r.passage.urn)" :class="{ active : r.active }">{{ r.passage.refs.start.human_reference }}</router-link>
            </li>
          </template>
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

function visibleInContainer(container, el) {
  const cTop = container.scrollTop;
  const cBottom = cTop + container.clientHeight;
  const eTop = el.offsetTop;
  const eBottom = eTop + el.clientHeight;
  return (eTop >= cTop && eBottom <= cBottom);
}

export default {
  store,
  mixins: [
    ReaderNavigationMixin,
  ],
  watch: {
    passage() {
      if (this.passage.ready) {
        this.results = this.markActive(this.results);
        this.$nextTick(this.scrollToActive);
      }
    },
    query: 'updateSearch',
    activeResults: 'updateHighlights',
  },
  created() {
    this.chunkSize = 200;
    this.initialTextSearch();
  },
  data() {
    return {
      query: this.$store.state.route.query.q,
      totalCount: null,
      results: [],
      loading: false,
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
        this.initialTextSearch()
          .then(() => {
            this.$router.push({
              name: 'reader',
              params: this.$store.state.route.params,
              query: { ...this.$store.state.route.query, q: query },
            });
          });
      },
      250,
    ),
    initialTextSearch() {
      // add pivot to dynamically modify offset around the passage
      // enables us to scroll to passages not in the first page
      // of results.
      this.loading = true;
      this.offsetMap = new Set();
      const opts = {
        size: this.chunkSize,
        pivot: this.passage.urn.toString(),
      };
      return this.textSearch(opts).then((res) => {
        this.firstOffset = res.pivot.start_offset;
        this.lastOffset = res.pivot.end_offset;
        this.totalCount = res.total_count;
        this.results = this.markActive(res.results);
        this.loading = false;
        this.$nextTick(() => {
          this.scrollToActive();
          if (res.results.length < this.totalCount) {
            this.infiniteScroll();
          }
        });
        this.$forceUpdate();
      });
    },
    textSearch({ offset = 0, size, pivot }) {
      return new Promise((resolve) => {
        if (!this.passage.ready) {
          resolve();
          return;
        }
        const params = {
          q: this.query.trim(),
          size,
          offset,
          pivot,
          text: this.passage.urn.upTo('version'),
        };
        resolve(sv.textSearch(params));
      });
    },
    previousPage() {
      const offset = Math.max(0, this.firstOffset - this.chunkSize);
      const size = this.chunkSize - ((this.firstOffset - this.chunkSize) * -1);
      return this.fetchPage('prepend', offset, size).then(({ results }) => {
        this.firstOffset = offset;
        return { results };
      });
    },
    nextPage() {
      const offset = this.lastOffset + 1;
      const { chunkSize: size } = this;
      return this.fetchPage('append', offset, size).then(({ results }) => {
        this.lastOffset = offset + (results.length - 1);
        return { results };
      });
    },
    fetchPage(op, offset, size) {
      return new Promise((resolve, reject) => {
        if (this.offsetMap.has(offset) || size <= 0) {
          return resolve({ results: [] });
        }
        const p = { size, offset };
        return this.textSearch(p)
          .then(({ results }) => {
            if (op === 'prepend') {
              this.results = this.markActive([...results, ...this.results]);
            } else if (op === 'append') {
              this.results = this.markActive([...this.results, ...results]);
            }
            this.offsetMap.add(offset);
            resolve({ results });
          })
          .catch(reject);
      });
    },
    markActive(results) {
      return results.map((result) => {
        let start;
        if (this.passage.urn.reference.includes('-')) {
          [start] = this.passage.urn.reference.split('-');
        } else {
          start = this.passage.urn.reference;
        }
        const current = `${this.passage.urn.upTo('version')}:${start}`;
        if (result.passage.urn === current) {
          return { ...result, active: true };
        }
        if (result.active === true) {
          return { ...result, active: false };
        }
        return result;
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
    isLast(idx) {
      return idx === this.results.length - 1;
    },
    activeItemElement() {
      const el = this.$refs.items.querySelector('li > a.active');
      if (el) {
        return el;
      }
      return null;
    },
    scrollToActive() {
      const activeEl = this.activeItemElement();
      if (activeEl) {
        const container = this.$refs.body.parentElement;
        if (!visibleInContainer(container, activeEl)) {
          container.scrollTop = activeEl.offsetTop - 50;
        }
      }
    },
    infiniteScroll() {
      let first;
      let last;
      if (this.observer !== undefined) {
        this.observer.disconnect();
      }
      const observer = new IntersectionObserver(
        (changes) => {
          changes.forEach((change) => {
            if (!change.isIntersecting || change.time < 4000) {
              return;
            }
            if (change.target === first) {
              observer.unobserve(first);
              this.previousPage().then(({ results }) => {
                if (results.length > 0) {
                  this.$nextTick(() => {
                    first = this.$refs.items.querySelector('li.first');
                    observer.observe(first);
                  });
                }
              });
            }
            if (change.target === last) {
              observer.unobserve(last);
              this.nextPage().then(({ results }) => {
                if (results.length > 0) {
                  this.$nextTick(() => {
                    last = this.$refs.items.querySelector('li.last');
                    observer.observe(last);
                  });
                }
              });
            }
          });
        },
        {
          root: this.$refs.body.parentElement,
          threshold: 1,
        },
      );
      first = this.$refs.items.querySelector('li.first');
      observer.observe(first);
      last = this.$refs.items.querySelector('li.last');
      observer.observe(last);
      this.observer = observer;
    },
  },
  components: {
    widget,
  },
};
</script>
