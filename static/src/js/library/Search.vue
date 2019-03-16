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
          <div class="search-pagination">
            <div>
              Showing <b>{{ start_index }}</b>&ndash;<b>{{ end_index }}</b> of <b>{{ total_results }}</b>
            </div>
            <!-- previous -->
            <div>
              <span v-if="page_num > 1">
                <a href="#"><i class="fa fa-step-backward"></i></a>
                <a href="#"><i class="fa fa-backward"></i></a>
              </span>
              <span v-else>
                <span class="text-muted"><i class="fa fa-step-backward"></i></span>
                <span class="text-muted"><i class="fa fa-backward"></i></span>
              </span>
              <!-- current -->
              <span class="current">
                page <b>{{ page_num }}</b> of <b>{{ total_pages }}</b>
              </span>
              <!-- next -->
              <span v-if="page_num + 1 <= total_pages">
                <span v-on:click="showNextPage"><i class="fa fa-forward" style="cursor:pointer;color:#B45141;"></i></span>
                <a href="#"><i class="fa fa-step-forward"></i></a>
              </span>
              <span v-else>
                <span class="text-muted"><i class="fa fa-forward"></i></span>
                <span class="text-muted"><i class="fa fa-step-forward"></i></span>
              </span>
            </div>
          </div>
          <div>
            <div class="result" v-for="result in results" :key="result.passage.url">
              <div class="passage-heading">
                <h2><a href="#">something</a></h2>
              </div>
              <div class="content">
                <p>something</p>
              </div>
            </div>
          </div>
          <div class="search-pagination">
            <div>
              Showing <b>{{ start_index }}</b>&ndash;<b>{{ end_index }}</b> of <b>{{ total_results }}</b>
            </div>
            <!-- previous -->
            <div>
              <span v-if="page_num > 1">
                <a href="#"><i class="fa fa-step-backward"></i></a>
                <a href="#"><i class="fa fa-backward"></i></a>
              </span>
              <span v-else>
                <span class="text-muted"><i class="fa fa-step-backward"></i></span>
                <span class="text-muted"><i class="fa fa-backward"></i></span>
              </span>
              <!-- current -->
              <span class="current">
                page <b>{{ page_num }}</b> of <b>{{ total_pages }}</b>
              </span>
              <!-- next -->
              <span v-if="page_num + 1 <= total_pages">
                <a href="#"><i class="fa fa-forward"></i></a>
                <a href="#"><i class="fa fa-step-forward"></i></a>
              </span>
              <span v-else>
                <span class="text-muted"><i class="fa fa-forward"></i></span>
                <span class="text-muted"><i class="fa fa-step-forward"></i></span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import constants from '../constants';
import api from '../api';

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
      results: []
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
    showNextPage() {
      const query = this.$store.state.reader.searchQuery;
      if (query !== '') {
        // move to an action
        const params = {
          kind: this.$store.state.reader.searchType,
          q: query,
          page_num: 2,
          start_index: this.start_index + 10,
          end_index: this.end_index + 10,
        }
        api.searchText(params, 'search/text/', result => {
          this.showSearchResults = true;
          this.total_pages = result.total_pages;
          this.total_results = result.total_results;
          this.results = result.results;
          this.page_num += 1;
          this.start_index +=10;
          this.end_index += 10,
          this.$forceUpdate();
        });
      }
    }
  },
};
</script>
