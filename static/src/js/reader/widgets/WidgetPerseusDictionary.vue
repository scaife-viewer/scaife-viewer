<template>
  <base-widget class="perseus-dictionary">
    <span slot="header">Perseus Dictionaries</span>
    <div slot="body">
      <div>
        <select v-model="selectedDictionary">
          <option disabled value="">Please select a dictionary</option>
          <option
            v-for="dictionary in availableDictionaries"
            :key="dictionary.urn"
            :value="dictionary.slug"
            >{{ dictionary.label }}</option
          >
        </select>
        <div class="search-input mt-2">
          <input
            v-model="query"
            type="text"
            class="form-control form-control-sm"
          />
        </div>

        <details v-for="result in results" :key="result.urn">
          <summary>{{ result.headword }} ({{ result.intro_text }})</summary>
          <div v-for="sense in result.data.senses" :key="sense.urn" class="senses">
            <div v-for="child in sense.children" :key="child.urn">
              <span v-html="child.definition" />
            </div>
          </div>
        </details>
        <div v-if="totalPages > 1">
          <a v-on:click="previousPage" :style="{ cursor: currentPage - 1 > 0 ? 'pointer' : 'auto' }">
            <span class="text-muted"><i class="fa fa-chevron-left"></i></span>
          </a>
          <a v-on:click="nextPage" :style="{ cursor: currentPage + 1 < totalPages ? 'pointer' : 'auto' }">
            <span class="text-muted"><i class="fa fa-chevron-right"></i></span>
          </a>
        </div>
      </div>
    </div>
  </base-widget>
</template>

<script>
import api from "../../api";

const debounce = require("lodash.debounce");

export default {
  name: "widget-perseus-dictionary",
  computed: {
    availableDictionaries() {
      return this.$store.state.reader.availableDictionaries;
    },
    selectedDictionary: {
      get() {
        return this.dictionary;
      },

      set(value) {
        this.dictionary = value;
      },
    },
    query: {
      get() {
        return this.q;
      },
      set(value) {
        this.q = value.trim();
      },
    },
  },
  data() {
    // TODO: Dictionaries should be able to declare relevant URN fragments
    const urn = this.$store.state.reader.leftPassage.urn.value;
    let dictionary = this.$store.state.reader.availableDictionaries[0].slug;
    let language = "unknown";

    if (urn.includes("-grc")) {
      language = "grc";
    } else if (urn.includes("-lat")) {
      language = "lat";
    }

    if (language === "grc") {
      dictionary = "lsj";
    }

    if (language === "lat") {
      dictionary = "lewis-and-short";
    }

    return {
      currentPage: 0,
      error: "",
      loading: false,
      q: "",
      results: [],
      dictionary,
      totalPages: 0,
    };
  },

  methods: {
    nextPage: debounce(function _nextPage() {
      if (this.currentPage + 1 > this.totalPages) {
        return;
      }

      api.searchPerseusDictionary(
        this.selectedDictionary,
        { q: this.query, page: this.currentPage + 1 },
        ({ current_page, results, total_pages }) => {
          this.results = results;
          this.currentPage = current_page;
          this.totalPages = total_pages;
        },
      );
    }, 250),
    previousPage: debounce(function _previousPage() {
      if (this.currentPage - 1 <= 0) {
        return;
      }

      api.searchPerseusDictionary(
        this.selectedDictionary,
        { q: this.query, page: this.currentPage - 1 },
        ({ current_page, results, total_pages }) => {
          this.results = results;
          this.currentPage = current_page;
          this.totalPages = total_pages;
        },
      );
    }, 250),
    updateSearch: debounce(function _updateSearch() {
      api.searchPerseusDictionary(
        this.selectedDictionary,
        { q: this.query },
        ({ current_page, results, total_pages }) => {
          this.results = results;
          this.currentPage = current_page;
          this.totalPages = total_pages;
        },
      );
    }, 250),
  },

  watch: {
    query: "updateSearch",
  },
};
</script>

<style>
lem {
  font-weight: bold;
}

.mt-2 {
  margin-top: 2rem;
}
</style>
