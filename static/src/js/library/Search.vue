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
      <form class="search-form" v-on:submit.prevent="onSubmit">
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
      <div v-if="showSearchResults" class="row">
        <div class="col-sm-3">
          <h5>Text Groups</h5>
          <div class="list-group">
            <a href="#" class="list-group-item d-flex justify-content-between align-items-center">
              <span>Sample</span>
              <span class="badge badge-primary badge-pill">20</span>
            </a>
          </div>
        </div>
        <div class="col-sm-9">
          <search-pagination
            :start_index=start_index
            :end_index=end_index
            :total_results=total_results
            :page_num=page_num
            :total_pages=total_pages
            :showNextPrevPage=showNextPrevPage
          />
          <div>
            <div class="result" v-for="result in results" :key="result.url">
              <div class="passage-heading">
                <h2><a :href="result.url">{{ result.url }}</a></h2>
              </div>
              <div class="content">
                <p v-html="result.content"></p>
              </div>
            </div>
          </div>
          <search-pagination
            :start_index=start_index
            :end_index=end_index
            :total_results=total_results
            :page_num=page_num
            :total_pages=total_pages
            :showNextPrevPage=showNextPrevPage
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

export default {
  name: 'search-view',
  data() {
    return {
      page_num: 1,
      showSearchResults: false,
      start_index: 1,
      end_index: 10,
      total_pages: 0,
      total_results: 0,
      results: [],
    };
  },
  computed: {
    searchQuery() {
      return this.$store.state.reader.searchQuery;
    },
    searchType() {
      return this.$store.state.reader.searchType;
    },
  },
  methods: {
    handleSearchQueryChange(e) {
      this.$store.commit(`reader/${constants.SET_SEARCH_QUERY}`, { query:  e.target.value });
    },
    handleTypeChange(e) {
      this.$store.commit(`reader/${constants.SET_SEARCH_TYPE}`, { type:  e.target.name });
    },
    onSubmit() {
      const query = this.$store.state.reader.searchQuery;
      if (query !== '') {
        // move to an action
        const params = {
          kind: this.$store.state.reader.searchType,
          q: query,
          page_num: this.page_num,
          start_index: 1,
          end_index: 10
        }
        api.searchText(params, 'search/text/', result => {
          this.showSearchResults = true;
          this.total_pages = result.total_pages;
          this.total_results = result.total_results;
          this.results = result.results;
        });
      }
    },
    showNextPrevPage(direction) {
      const query = this.$store.state.reader.searchQuery;
      if (query !== '') {
        let newPageNum = this.page_num + 1;
        let newStartIndex = this.start_index + 10;
        let newEndIndex = this.end_index + 10;
        if (direction === 'prev') {
          newPageNum = this.page_num - 1;
          newStartIndex = this.start_index - 10;
          newEndIndex = this.end_index - 10;
          if (parseInt(this.page_num) === parseInt(this.total_pages)) {
            newEndIndex = (newStartIndex + 10) - 1;
          }
        }
        // move to an action
        const params = {
          kind: this.$store.state.reader.searchType,
          q: query,
          page_num: newPageNum,
          start_index: newStartIndex,
          end_index: newEndIndex,
        }
        api.searchText(params, 'search/text/', result => {
          this.showSearchResults = true;
          this.total_pages = result.total_pages;
          this.total_results = result.total_results;
          this.results = result.results;
          this.page_num = newPageNum;
          this.start_index = newStartIndex;
          this.end_index = newEndIndex;
          if (parseInt(newPageNum) === parseInt(this.total_pages)) {
            this.end_index = result.total_results;
          }
        });
      }
    }
  },
  components: {
    SearchPagination,
  },
};
</script>
