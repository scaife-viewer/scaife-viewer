<template>
  <widget class="search">
    <span slot="header">
      Text Search
      <span v-if="query && totalCount !== null" class="result-count">({{ totalCount }})</span>
    </span>
    <div slot="sticky">
      <div class="search-input">
        <input v-model="query" type="text" class="form-control form-control-sm" />
        <input type="radio" id="kind-form" name="kind" value="form" v-model="queryKind"><label for="kind-form">Form</label>
        <input type="radio" id="kind-lemma" name="kind" value="lemma" v-model="queryKind"><label for="kind-lemma">Lemma (Greek only)</label>
      </div>
    </div>
    <div slot="body" ref="body">
      <div class="search-hits">
        <text-loader v-if="loading" size="7px" margin="1px" />
        <div v-else-if="error"><small class="text-danger"><b>Error:</b> {{ error }}</small></div>
        <template v-else>
          <p class="instructions" v-if="query === '' && results.length === 0">Use text input above to find text in this version.</p>
          <p class="no-results" v-else-if="results.length === 0">No results found.</p>
          <ul v-else ref="items">
            <li v-for="(r, idx) in results" :class="{ first: idx === 0, last: isLast(idx) }" :key="r.passage.urn">
              <router-link :to="toPassage(r.passage.urn)" :class="{ active : r.active }">{{ r.passage.refs.start.human_reference }}</router-link>
            </li>
          </ul>
        </template>
      </div>
    </div>
  </widget>
</template>

<script>
import sv from '../../scaife-viewer';
import store from '../../store';
import widget from '../widget';
import ReaderNavigationMixin from '../reader-navigation-mixin';
import TextLoader from '../text-loader';

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
    queryKind: 'updateSearch',
    activeResults: 'updateHighlights',
  },
  created() {
    this.chunkSize = 200;
    if (this.$store.state.route.query.q) {
      this.query = this.$store.state.route.query.q;
    }
    if (this.$store.state.route.query.qk) {
      this.queryKind = this.$store.state.route.query.qk;
    }
    if (this.query !== '') {
      this.initialTextSearch();
    }
  },
  data() {
    return {
      q: '',
      queryKind: 'form',
      totalCount: null,
      results: [],
      loading: false,
      error: '',
    };
  },
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
    query: {
      get() {
        return this.q;
      },
      set(value) {
        this.q = value.trim();
      },
    },
    activeResults() {
      return this.results.filter(({ active }) => active);
    },
  },
  methods: {
    updateSearch: debounce(
      function f() {
        this.initialTextSearch()
          .then(() => {
            this.$router.push({
              name: 'reader',
              params: this.$store.state.route.params,
              query: {
                ...this.$store.state.route.query,
                q: this.query,
                qk: this.queryKind,
              },
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
      this.error = '';
      this.totalCount = null;
      this.results = [];
      this.offsetMap = new Set();
      const opts = {
        size: this.chunkSize,
        pivot: this.passage.urn.toString(),
      };
      return this.textSearch(opts)
        .then((res) => {
          if (!res || res.results.length === 0) {
            this.totalCount = 0;
            this.loading = false;
          } else {
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
            // @@@ check if we really need to forceUpdate
            this.$forceUpdate();
          }
        })
        .catch((err) => {
          this.loading = false;
          this.error = err.message;
        });
    },
    textSearch({ offset = 0, size, pivot }) {
      return new Promise((resolve, reject) => {
        if (!this.passage.ready) {
          resolve(Promise.resolve(null));
        } else if (this.query === '') {
          resolve(Promise.resolve(null));
        } else {
          const params = {
            q: this.query,
            kind: this.queryKind,
            size,
            offset,
            pivot,
            fields: '',
            text: this.passage.urn.upTo('version'),
          };
          sv.textSearch(params).then(resolve, reject);
        }
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
          .then(({ res: { results } }) => {
            if (op === 'prepend') {
              this.results = this.markActive([...results, ...this.results]);
            } else if (op === 'append') {
              this.results = this.markActive([...this.results, ...results]);
            }
            this.offsetMap.add(offset);
            resolve({ results });
          })
          .catch((err) => {
            this.error = err.message;
            reject(err);
          });
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
      this.activeResults.forEach(({ passage }) => {
        const params = {
          q: this.query,
          kind: this.queryKind,
          fields: 'highlights',
          passage: passage.urn,
          size: 1,
        };
        sv.textSearch(params).then(({ results }) => {
          const { highlights } = results[0];
          this.$store.commit('reader/setAnnotations', {
            tokens: highlights.map(({ w, i }) => `${w}[${i}]`),
            key: 'highlighted',
            value: true,
          });
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
                    this.$refs.body.parentElement.scrollTop = first.offsetTop - 5;
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
    TextLoader,
  },
};
</script>
