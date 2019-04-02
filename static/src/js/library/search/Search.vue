<template>
  <section>
    <div class="container">
      <div class="search-guide">
        <h3>Search Guide</h3>
        <div class="row">
          <div class="col-md-6">
            <kbd>+</kbd> signifies AND operation<br>
            <kbd>|</kbd> signifies OR operation<br>
            <kbd>-</kbd> negates a single token<br>
            <kbd>"</kbd> wraps a number of tokens to signify a phrase for searching<br>
          </div>
          <div class="col-md-6">
            <kbd>*</kbd> at the end of a term signifies a prefix query<br>
            <kbd>(</kbd> and <kbd>)</kbd> signify precedence<br>
            <kbd>~<var>num</var></kbd> after a word signifies edit distance (fuzziness)<br>
            <kbd>~<var>num</var></kbd> after a phrase signifies slop amount<br>
          </div>
        </div>
      </div>
      <form class="search-form" v-on:submit.prevent="handleSearch(0)">
        <div class="form-group">
          <input type="text" class="form-control" placeholder="Search..." :value="searchQuery" @input="handleSearchQueryChange">
          <input
            type="radio"
            id="kind-form"
            name="form"
            :value="searchType"
            @input="handleTypeChange"
            :checked="searchType=='form'"
          >
          <label for="kind-form">Form</label>
          <input
            type="radio"
            id="kind-lemma"
            name="lemma"
            :value="searchType"
            @input="handleTypeChange"
            :checked="searchType=='lemma'"
          >
          <label for="kind-lemma">Lemma (Greek only)</label>
        </div>
      </form>
      <text-loader v-if="loading" size="7px" margin="1px" />
      <div v-if="showSearchResults" class="row">
        <div v-if="!results.length && !textGroups.length" class="col-sm-12 text-center">
          <p class="no-results">No results found. Please try again.</p>
        </div>
          <search-text-groups
            :textGroups=textGroups
            :handleSearch=handleSearch
            :showClear=showClear
            :showTextGroups=showTextGroups
            :handleshowTextGroupsChange=handleshowTextGroupsChange
          />
        <div v-if="results.length" class="col-md-9">
          <search-pagination
            :startIndex=startIndex
            :endIndex=endIndex
            :totalResults=totalResults
            :pageNum=pageNum
            :totalPages=totalPages
            :hasNext=hasNext
            :hasPrev=hasPrev
            :handleSearch=handleSearch
          />
          <div>
            <text-loader v-if="secondLoading" size="7px" margin="1px" />
            <div class="result" v-if="!secondLoading" v-for="result in results" :key="result.link">
              <div class="passage-heading">
                <h2>
                  <a :href="''+result.link+'?q='+searchQuery+'&amp;qk='+searchType+''">
                    <span v-for="breadcrumb in result.passage.text.ancestors" :key="breadcrumb.label">
                      {{ breadcrumb.label }},
                    </span>
                    <span>{{ result.passage.refs.start.human_reference }}</span>
                    <span v-if="result.passage.refs.end">
                      to {{ result.passage.refs.end.human_reference }}
                    </span>
                    <span v-if="!result.passage.refs.end">
                      ({{ result.passage.refs.start.reference }})
                    </span>
                    <span v-if="result.passage.refs.end">
                      ({{ result.passage.refs.start.reference }} to &ndash; {{ result.passage.refs.end.reference }})
                    </span>
                  </a>
                </h2>
              </div>
              <div class="content">
                <p v-for="result in result.content" :key="result">
                  <span v-html="result"></span>
                </p>
              </div>
            </div>
          </div>
          <search-pagination
            :startIndex=startIndex
            :endIndex=endIndex
            :totalResults=totalResults
            :pageNum=pageNum
            :totalPages=totalPages
            :hasNext=hasNext
            :hasPrev=hasPrev
            :handleSearch=handleSearch
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import constants from '../../constants';
import api from '../../api';
import SearchPagination from './SearchPagination.vue';
import SearchTextGroups from './SearchTextGroups.vue';
import TextLoader from '../../components/TextLoader.vue';

export default {
  name: 'search-view',
  data() {
    return {
      searchQuery: '',
      pageNum: null,
      startIndex: null,
      endIndex: null,
      totalPages: null,
      totalResults: null,
      results: [],
      textGroups: [],
      loading: false,
      secondLoading: false,
      showSearchResults: false,
      hasNext: false,
      hasPrev: false,
      searchType: 'form',
      showClear: false,
      tg: null,
      showTextGroups: false
    };
  },
  mounted() {
    const queryParams = this.$route.query;
    if (Object.entries(queryParams).length !== 0 && queryParams.constructor === Object) {
      this.searchQuery = queryParams.q;
      this.searchType = queryParams.kind || 'form';
      this.pageNum = queryParams.p;
      this.tg = queryParams.tg;
      this.handleSearch(this.pageNum, this.tg);
    }
  },
  methods: {
    handleSearchQueryChange(e) {
      this.searchQuery = e.target.value;
    },
    handleTypeChange(e) {
      this.searchType = e.target.name;
    },
    handleshowTextGroupsChange() {
      this.showTextGroups = !this.showTextGroups;
    },
    handleSearch(pageNum, urn=null) {
      const query = this.searchQuery;
      if (query !== '') {
        if (pageNum) {
          this.secondLoading = true;
          this.showClear = false;
        } else {
          this.loading = true;
          this.showSearchResults = false;
          this.showClear = false;
          this.tg = null;
          pageNum = 1;
          this.showTextGroups = false;
        }
        if (urn) {
          this.showClear = true;
          this.results = [];
          this.tg = urn;
        }
        if (this.tg) {
          this.showClear = true;
        }
        const params = {
          kind: this.searchType,
          q: query,
          page_num: pageNum,
          tg: this.tg,
        }
        api.searchText(params, 'search/text/', result => {
          this.showSearchResults = true;
          this.totalPages = result.page.num_pages;
          this.pageNum = result.page.number;
          this.startIndex = result.page.start_index;
          this.endIndex = result.page.end_index;
          this.hasNext = result.page.has_next;
          this.hasPrev = result.page.has_previous;
          this.totalResults = result.total_count;
          this.results = result.results;
          this.textGroups = result.text_groups
          this.secondLoading = false;
          this.loading = false;
          if (this.tg) {
            this.showClear = true;
          }
          // update url state
          this.$router.replace({
            query: {
              q: this.searchQuery,
              kind: this.searchType,
              p: this.pageNum,
              tg: this.tg
            }
          });
        });
      }
    },
  },
  components: {
    SearchPagination,
    SearchTextGroups,
    TextLoader
  },
};
</script>
