<template>
  <div class="library-component">
    <page-loader v-if="loading" />
    <div v-else-if="error" class="text-center"><b>Error</b>: {{ error }}</div>
    <template v-else>
      <h2>Text Groups and Works</h2>
      <div class="form-group">
        <div class="input-group">
          <input
            type="text"
            class="form-control"
            v-model="query"
            placeholder="Find a text group or work... (e.g. Plato or Apology)"
            ref="filter-input"
          >
          <div class="input-group-append" v-if="filtered">
            <button class="btn btn-outline-secondary" type="button" @click="clearQuery"><icon name="times"></icon></button>
          </div>
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
          <template v-for="textGroup in sortedTextGroups">
            <keep-alive>
              <library-text-group ref="collapsible" :textGroup="textGroup" :texts="versions" :filtered="filtered" :key="textGroup.urn" />
            </keep-alive>
          </template>
        </template>
        <div v-else-if="sortKind === 'work'" class="flat-work-list">
          <template v-for="work in sortedWorks">
            <keep-alive>
              <library-work :work="work" :text-groups="textGroups" :versions="versions" :filtered="filtered" :key="work.urn" />
            </keep-alive>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import constants from '../constants';
import LibraryTextGroup from './LibraryTextGroup.vue';
import LibraryWork from './LibraryWork.vue';

const debounce = require('lodash.debounce');
import gql from 'graphql-tag';


export default {
  // created() {
  //   this.loading = true;
  //   this.$store.dispatch(constants.LIBRARY_LOAD_TEXT_GROUP_LIST)
  //     .then(() => {
  //       // delay for vuex store update
  //       setTimeout(()=> {
  //         // this.loading = false;
  //         this.$nextTick(() => {
  //           this.$refs['filter-input'].focus();
  //         });
  //       }, 100)
  //     })
  //     // .catch((err) => {
  //     //   this.loading = false;
  //     //   this.error = err.message;
  //     // });
  // },
  data() {
    return {
      // loading: false,
      error: '',
      query: '',
      trimmedQuery: '',
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
    loading() {
      if (!this.loading) {
        this.$nextTick(() => {
          this.$refs['filter-input'].focus();
        });
      }
    },
  },
  computed: {
    loading() {
      return !this.gqlData;
    },
    textGroups() {
      const textGroups = [];
      const initialTextGroups = this.gqlData
        ? this.gqlData.textGroups.edges.map(textGroup => textGroup.node)
        : [];
      initialTextGroups.forEach((textGroup) => {
        textGroups.push({
          ...textGroup,
          works: this.getWorks(textGroup),
        });
      });
      return textGroups;
    },
    filteredTextGroups() {
      if (!this.filtered) {
        return this.textGroups;
      }
      const filteredTextGroups = [];
      this.textGroups.forEach((textGroup) => {
        if (textGroup.label.toLowerCase().indexOf(this.trimmedQuery.toLowerCase()) !== -1) {
          filteredTextGroups.push(textGroup);
        } else {
          const works = textGroup.works.filter((work) => {
            return work.label.toLowerCase().indexOf(this.trimmedQuery.toLowerCase()) !== -1;
          });
          if (works.length > 0) {
            filteredTextGroups.push({ ...textGroup, works });
          }
        }
      });
      return filteredTextGroups;
    },
    sortedTextGroups() {
      return this.sortKind === 'text-group' ? this.alphaSortedTextGroups : this.URNSortedTextGroups;
    },
    URNSortedTextGroups() {
      return [...this.filteredTextGroups].sort((a, b) => a.urn.localeCompare(b.urn));
    },
    alphaSortedTextGroups() {
      return [...this.filteredTextGroups].sort((a, b) => a.label.localeCompare(b.label));
    },
    works() {
      return this.gqlData
        ? this.gqlData.works.edges.map(work => work.node)
        : [];
    },
    filteredWorks() {
      return this.filtered ? this.works.filter(work => work.label.toLowerCase().indexOf(this.trimmedQuery.toLowerCase()) !== -1) : this.works;
    },
    sortedWorks() {
      return [...this.filteredWorks].sort((a, b) => a.label.localeCompare(b.label));
    },
    versions() {
      return this.gqlData
        ? this.gqlData.versions.edges.map(version => version.node)
        : [];
    },
    sortKind() {
      return this.$store.state.library.sortKind;
    },
    collapsible() {
      return this.sortKind === 'cts-urn' || this.sortKind === 'text-group';
    },
    gqlQuery() {
      return gql`
        {
          textGroups {
            edges {
              node {
                label
                urn
              }
            }
          }
          works {
            edges{
              node {
                urn
                label
              }
            }
          }
          versions {
            edges {
              node {
                access
                urn
                label
                description
                lang
              }
            }
          }
        }`;
    },
  },
  methods: {
    clearQuery() {
      this.query = '';
    },
    filter: debounce(
      function f() {
        this.trimmedQuery = this.query.trim();
        if (this.trimmedQuery === '') {
          this.filtered = false;
        } else {
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
      this.$store.commit(constants.SET_LIBRARY_SORT, { kind });
    },
    safeURN(urn) {
      // @@@ maintain backwards compatability
      return urn.endsWith(':') ? urn.slice(0, -1) : urn;
    },
    getWorks(textGroup) {
      const textGroupUrn = this.safeURN(textGroup.urn);
      return this.works ? this.works.filter(work => work.urn.startsWith(textGroupUrn)) : this.works;
    },
  },
  components: {
    LibraryTextGroup,
    LibraryWork,
  },
};
</script>
