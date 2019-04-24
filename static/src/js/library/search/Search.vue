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
      <text-loader v-if="firstLoading" size="7px" margin="1px" />
      <div v-if="showSearchResults" class="row">
        <div v-if="!results.length && !textGroups.length" class="col-sm-12 text-center">
          <p class="no-results">No results found. Please try again.</p>
        </div>
        <div v-if="textGroups.length" class="col-md-3">
          <search-text-groups
            :textGroups=textGroups
            :handleSearch=handleSearch
            :showClearTextGroup=showClearTextGroup
            :showTextGroups=showTextGroups
            :handleShowTextGroupsChange=handleShowTextGroupsChange
            :clearWorkGroups=clearWorkGroups
          />
          <search-work-groups
            v-if="workGroups.length"
            :workGroups=workGroups
            :handleSearch=handleSearch
            :showClearWorkGroup=showClearWorkGroup
            :showWorkGroups=showWorkGroups
            :handleShowWorkGroupsChange=handleShowWorkGroupsChange
            :textGroup=textGroup
          />
        </div>
        <div v-if="results.length || textGroups.length" class="col-md-9">
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
          <text-loader v-if="secondLoading" size="7px" margin="1px" />
          <div>
            <search-results
              :secondLoading=secondLoading
              :results=results
              :createPassageLink=createPassageLink
            />
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
import SearchWorkGroups from './SearchWorkGroups.vue';
import SearchResults from './SearchResults.vue';
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
      workGroups: [],
      firstLoading: false,
      secondLoading: false,
      showSearchResults: false,
      hasNext: false,
      hasPrev: false,
      searchType: 'form',
      showClearTextGroup: false,
      showClearWorkGroup: false,
      textGroup: null,
      showTextGroups: false,
      showWorkGroups: false
    };
  },
  mounted() {
    const queryParams = this.$route.query;
    if (Object.entries(queryParams).length !== 0 && queryParams.constructor === Object) {
      this.searchQuery = queryParams.q;
      this.searchType = queryParams.kind || 'form';
      this.pageNum = queryParams.p;
      this.textGroup = queryParams.tg;
      this.workGroup = queryParams.wg;
      this.handleSearch(this.pageNum, this.textGroup, this.workGroup);
    }
  },
  methods: {
    handleSearchQueryChange(e) {
      this.searchQuery = e.target.value;
    },
    handleTypeChange(e) {
      this.searchType = e.target.name;
    },
    handleShowTextGroupsChange() {
      this.showTextGroups = !this.showTextGroups;
      this.showWorkGroups = !this.showWorkGroups;
    },
    handleShowWorkGroupsChange() {
      this.showWorkGroups = !this.showWorkGroups;
    },
    clearWorkGroups() {
      this.workGroups = [];
    },
    handleSearch(pageNum, textGroup=null, workGroup=null) {
      const query = this.searchQuery;
      if (query !== '') {
        if (pageNum) {
          if (!this.results.length) {
            this.firstLoading = true;
          } else {
            this.secondLoading = true;
          }
          this.showClearTextGroup = false;
          this.showClearWorkGroup = false;
        } else {
          this.firstLoading = true;
          this.showSearchResults = false;
          this.showClearTextGroup = false;
          this.showClearWorkGroup = false;
          this.textGroup = null;
          this.workGroup = null;
          pageNum = 1;
          this.showTextGroups = false;
          this.showWorkGroups = false;
        }
        if (textGroup) {
          this.showClearTextGroup = true;
          this.results = [];
          this.textGroup = textGroup;
        }
        if (workGroup) {
          this.showClearWorkGroup = true;
          this.results = [];
          this.workGroup = workGroup;
        }
        if (this.textGroup) {
          this.showClearTextGroup = true;
        }
        const params = {
          kind: this.searchType,
          q: query,
          page_num: pageNum,
          text_group: this.textGroup,
          work_group: this.workGroup,
          type: 'library',
        }
        api.searchText(params, 'search/json/', result => {
          console.log(result)
          this.showSearchResults = true;
          this.totalPages = result.page.num_pages;
          this.pageNum = result.page.number;
          this.startIndex = result.page.start_index;
          this.endIndex = result.page.end_index;
          this.hasNext = result.page.has_next;
          this.hasPrev = result.page.has_previous;
          this.totalResults = result.total_count;
          this.results = result.results;
          this.textGroups = result.text_groups;
          this.secondLoading = false;
          this.firstLoading = false;
          if (this.textGroup) {
            this.showClearTextGroup = true;
            this.workGroups = result.work_groups;
          }
          if (this.workGroup) {
            this.showClearWorkGroup = true;
          }
          // update url state
          const urlState = {
            q: this.searchQuery,
            kind: this.searchType,
            p: this.pageNum
          }
          if (this.textGroup) {
            urlState.tg = this.textGroup;
          }
          if (this.workGroup) {
            urlState.wg = this.workGroup;
          }
          this.$router.replace({
            query: urlState,
          });
        });
      }
    },
    createPassageLink(link) {
      return `${link}?q=${this.searchQuery}&amp;qk=${this.searchType}`;
    }
  },
  components: {
    SearchPagination,
    SearchTextGroups,
    SearchWorkGroups,
    SearchResults,
    TextLoader,
  },
};
</script>
