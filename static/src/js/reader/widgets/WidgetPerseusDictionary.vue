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

        <div v-for="result in results" :key="result.urn">{{ result.headword }}</div>
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
      error: "",
      loading: false,
      q: "",
      results: [],
      dictionary,
      totalCount: null,
    };
  },

  methods: {
    updateSearch: debounce(function _updateSearch() {
      api.searchPerseusDictionary(
        this.selectedDictionary,
        { q: this.query },
        ({ current_page, results, total_pages }) => {
          this.results = results;
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
