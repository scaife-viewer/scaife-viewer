<template>
  <div class="library-component">
    <template v-if="loading">
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <template v-else>
      <div class="form-group">
        <div class="input-group">
          <input
            type="text"
            class="form-control"
            v-model="query"
            placeholder="Find a text group or work... (e.g. Plato or Apology)"
            ref="filter-input"
          >
          <span class="input-group-addon" v-if="filtered">
            <i class="fa fa-times" @click="clearQuery"></i>
          </span>
        </div>
      </div>
      <div class="controls">
        <div class="toggle-all">
          <template v-if="!filtered && collapsible">
          <span @click="expandAll">expand all</span> | <span @click="collapseAll">collapse all</span>
          </template>
        </div>
        <div class="sort">
          sort by:
          <span @click="sort('text-group')" :class="{ active: sortKind === 'text-group' }">text group</span> |
          <span @click="sort('cts-urn')" :class="{ active: sortKind === 'cts-urn' }">CTS URN</span> |
          <span @click="sort('work')" :class="{ active: sortKind === 'work' }">work</span>
        </div>
      </div>
      <div :class="['text-groups', { filtered }]">
        <template v-if="sortKind === 'cts-urn' || sortKind === 'text-group'">
          <template v-for="textGroup in textGroups">
            <keep-alive>
              <library-text-group ref="collapsible" :textGroup="textGroup" :filtered="filtered" :key="textGroup.urn" />
            </keep-alive>
          </template>
        </template>
        <div v-else-if="sortKind === 'work'" class="flat-work-list">
          <template v-for="work in works">
            <keep-alive>
              <library-work :work="work" :filtered="filtered" :key="work.urn" />
            </keep-alive>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import store from '../store';
import LibraryTextGroup from './LibraryTextGroup';
import LibraryWork from './LibraryWork';

const debounce = require('lodash.debounce');

export default {
  store,
  created() {
    this.loading = true;
    this.$store.dispatch('loadTextGroupList').then(() => {
      this.loading = false;
      this.$nextTick(() => {
        this.$refs['filter-input'].focus();
      });
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
    sortKind() {
      this.filter();
    },
  },
  computed: {
    textGroups() {
      if (this.sortKind === 'text-group') {
        return this.$store.getters.sortedByTextGroup;
      }
      return this.$store.getters.sortedByURN;
    },
    works() {
      return this.$store.getters.sortedByWork;
    },
    sortKind() {
      return this.$store.state.library.sortKind;
    },
    collapsible() {
      return this.sortKind === 'cts-urn' || this.sortKind === 'text-group';
    },
  },
  methods: {
    clearQuery() {
      this.query = '';
    },
    filter: debounce(
      function f() {
        const query = this.query.trim();
        let kind = 'TextGroups';
        if (this.sortKind === 'work') {
          kind = 'TextGroupWorks';
        }
        if (query === '') {
          this.$store.dispatch(`reset${kind}`);
          this.filtered = false;
        } else {
          this.$store.dispatch(`filter${kind}`, query);
          this.filtered = true;
        }
      },
      250,
    ),
    collapseAll() {
      this.$refs.collapsible.forEach((c) => {
        c.open = false;
      });
    },
    expandAll() {
      this.$refs.collapsible.forEach((c) => {
        c.open = true;
      });
    },
    sort(kind) {
      this.$store.commit('setLibrarySort', { kind });
    },
  },
  components: {
    LibraryTextGroup,
    LibraryWork,
  },
};
</script>
