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
        <div v-if="!results.length && !textGroups.length" class="col-sm-12 text-center">
          <p class="no-results">No results found. Please try again.</p>
        </div>
        <div v-if="textGroups.length" class="col-sm-3">
          <h5 v-if="showClear">
            <span>Text Groups</span>
            &nbsp;
            <small style="cursor:pointer;color:#B45141;" v-on:click="handleSearch">clear</small>
          </h5>
          <h5 v-if="!showClear">Text Groups</h5>
          <div class="list-group">
            <a
              v-for="ftg in textGroups"
              :key="ftg.text_group.urn"
              class="list-group-item d-flex justify-content-between align-items-center"
              style="cursor:pointer;color:#B45141;"
              v-on:click="handleViewTextGroup(ftg.text_group.urn)"
            >
              <span>{{ ftg.text_group.label }}</span>
              <span class="badge badge-primary badge-pill">{{ ftg.count }}</span>
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
                    <span>{{ result.passage.refs.start.reference }}</span>
                    <span v-if="result.passage.refs.end">
                      to &ndash; {{ result.passage.refs.end.reference }}
                    </span>
                  </a>
                </h2>
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
      textGroups: [],
      loading: false,
      secondLoading: false,
      showSearchResults: false,
      hasNext: false,
      hasPrev: false,
      searchType: 'form',
      showClear: false
    };
  },
  methods: {
    handleSearchQueryChange(e) {
      this.searchQuery = e.target.value;
      // this.$store.commit(`reader/${constants.SET_SEARCH_QUERY}`, { query:  e.target.value });
    },
    handleTypeChange(e) {
      this.searchType = e.target.name;
      // this.$store.commit(`reader/${constants.SET_SEARCH_TYPE}`, { type:  e.target.name });
    },
    handleSearch() {
      const query = this.searchQuery;
      if (query !== '') {
        this.loading = true;
        this.showSearchResults = false;
        this.showClear = false;
        const params = {
          kind: this.searchType,
          q: query,
          page_num: 1,
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
          this.loading = false;
        });
      }
    },
    handlePrevNext(newPageNum) {
      this.secondLoading = true;
      const params = {
        kind: this.searchType,
        q: this.searchQuery,
        page_num: newPageNum,
      }
      api.searchText(params, 'search/text/', result => {
        this.totalPages = result.page.num_pages;
        this.pageNum = result.page.number;
        this.startIndex = result.page.start_index;
        this.endIndex = result.page.end_index;
        this.hasNext = result.page.has_next;
        this.hasPrev = result.page.has_previous;
        this.totalResults = result.total_count;
        this.results = result.results;
        this.secondLoading = false;
      });
    },
    handleViewTextGroup(urn) {
      this.loading = true;
      this.showClear = true;
      this.results = [];
      const params = {
        kind: this.searchType,
        q: this.searchQuery,
        page_num: 1,
        tg: urn
      }
      api.searchText(params, 'search/text/', result => {
        this.totalPages = result.page.num_pages;
        this.pageNum = result.page.number;
        this.startIndex = result.page.start_index;
        this.endIndex = result.page.end_index;
        this.hasNext = result.page.has_next;
        this.hasPrev = result.page.has_previous;
        this.totalResults = result.total_count;
        this.results = result.results;
        this.textGroups = result.text_groups
        this.loading = false;
      });
    },
  },
  components: {
    SearchPagination,
    TextLoader
  },
};
</script>
