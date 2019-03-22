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
      <form class="search-form" v-on:submit.prevent="handleSearch">
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
        <div v-if="!results.length" class="col-sm-12 text-center">
          <p class="no-results">No results found. Please try again.</p>
        </div>
        <div v-if="results.length" class="col-sm-3">
          <h5>Text Groups</h5>
          <div class="list-group">
            <a href="#" class="list-group-item d-flex justify-content-between align-items-center">
              <span>Sample</span>
              <span class="badge badge-primary badge-pill">20</span>
            </a>
          </div>
        </div>
        <div v-if="results.length" class="col-sm-9">
          <search-pagination
            :startIndex=startIndex
            :endIndex=endIndex
            :totalResults=totalResults
            :pageNum=pageNum
            :totalPages=totalPages
            :hasNext=hasNext
            :hasPrev=hasPrev
            :handlePrevNext=handlePrevNext
          />
          <div>
            <text-loader v-if="secondLoading" size="7px" margin="1px" />
            <div class="result" v-if="!secondLoading" v-for="result in results" :key="result.url">
              <div class="passage-heading">
                <h2><a :href="result.url">{{ result.url }}</a></h2>
              </div>
              <div class="content">
                <p v-html="result.content"></p>
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
            :handlePrevNext=handlePrevNext
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import constants from '../constants';
import api from '../api';
import SearchPagination from './SearchPagination.vue';
import TextLoader from '../components/TextLoader.vue';

export default {
  // TODO: add global state mgmt
  name: 'search-view',
  data() {
    return {
      searchQuery: '',
      pageNum: 1,
      startIndex: null,
      endIndex: null,
      totalPages: null,
      totalResults: null,
      results: [],
      loading: false,
      secondLoading: false,
      showSearchResults: false,
      hasNext: false,
      hasPrev: false,
    };
  },
  computed: {
    // searchQuery() {
    //   return this.$store.state.reader.searchQuery;
    // },
    searchType() {
      return this.$store.state.reader.searchType;
    },
  },
  methods: {
    handleSearchQueryChange(e) {
      this.searchQuery = e.target.value;
      // this.$store.commit(`reader/${constants.SET_SEARCH_QUERY}`, { query:  e.target.value });
    },
    handleTypeChange(e) {
      this.$store.commit(`reader/${constants.SET_SEARCH_TYPE}`, { type:  e.target.name });
    },
    handleSearch() {
      const query = this.searchQuery;
      if (query !== '') {
        this.loading = true;
        this.showSearchResults = false;
        const params = {
          kind: this.$store.state.reader.searchType,
          q: query,
          page_num: this.pageNum,
        }
        api.searchText(params, 'search/text/', result => {
          this.showSearchResults = true;
          this.totalPages = result.page.num_pages;
          this.pageNum = result.page.number;
          this.startIndex = result.page.start_index;
          this.endIndex = result.page.end_index;
          this.hasNext = result.page.has_next;
          this.hasPrev = result.page.has_previous;
          this.totalResults = result.count;
          this.totalPages = result.page.num_pages;
          this.results = result.results;
          this.loading = false;
        });
      }
    },
    handlePrevNext(newPageNum) {
      const query = this.searchQuery;
      if (query !== '') {
        this.secondLoading = true;
        const params = {
          kind: this.$store.state.reader.searchType,
          q: query,
          page_num: newPageNum,
        }
        api.searchText(params, 'search/text/', result => {
          this.totalPages = result.page.num_pages;
          this.pageNum = result.page.number;
          this.startIndex = result.page.start_index;
          this.endIndex = result.page.end_index;
          this.hasNext = result.page.has_next;
          this.hasPrev = result.page.has_previous;
          this.totalResults = result.count;
          this.totalPages = result.num_pages;
          this.results = result.results;
          this.secondLoading = false;
        });
      }
    },
  },
  components: {
    SearchPagination,
    TextLoader
  },
};
</script>
