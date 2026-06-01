<template>
  <base-widget class="perseus-dictionary">
    <span slot="header">Perseus Dictionaries</span>
    <div slot="body">
      <div>
        <select v-model="selectedDictionary" name="perseus-dictionary-select">
          <option disabled value="">Please select a dictionary</option>
          <option
            v-for="dictionary in availableDictionaries"
            :key="dictionary.urn"
            :value="dictionary.slug"
          >
            {{ dictionary.label }}
          </option>
        </select>
        <div class="search-input mt-2">
          <label
            >Search with <code>*</code> to match anywhere in the headword. E.g.,
            <code>*εχω</code> will match ἀπέχω etc.</label
          >
          <input
            v-model="query"
            type="text"
            class="form-control form-control-sm"
          />
        </div>

        <div class="loading-container mt-2" v-if="loading">
          <div class="dot" />
        </div>

        <div v-if="(results || []).length > 0 && q.length">
          <div v-for="result in results" :key="result.urn" class="mt-2">
            <details
              v-if="
                (result.data.senses || []).length > 0 &&
                (result.data.senses || []).some(
                  (s) => Boolean(s.definition) || (s.children || []).length > 0,
                )
              "
            >
              <summary>
                {{ result.headword_normalized }} ({{ result.intro_text }})
              </summary>
              <perseus-dictionary-sense
                v-for="sense in result.data.senses"
                :key="sense.urn"
                :children="sense.children"
                :citations="sense.citations"
                :definition="sense.definition"
                :label="sense.label"
                :urn="sense.urn"
              />
            </details>
            <div v-else>
              <span
                ><strong>{{ result.headword_normalized }}</strong
                >: <span v-html="result.intro_text"></span
              ></span>
            </div>
          </div>
        </div>
        <div v-else class="mt-2">
          <span v-if="q.length && !loading">No results found.</span>
        </div>
      </div>

      <div v-if="totalPages > 1 && q.length">
        <a
          v-on:click="previousPage"
          :style="{ cursor: currentPage - 1 > 0 ? 'pointer' : 'auto' }"
        >
          <span class="text-muted"><i class="fa fa-chevron-left"></i></span>
        </a>
        <a
          v-on:click="nextPage"
          :style="{ cursor: currentPage + 1 < totalPages ? 'pointer' : 'auto' }"
        >
          <span class="text-muted"><i class="fa fa-chevron-right"></i></span>
        </a>
      </div>
    </div>
  </base-widget>
</template>

<script>
import api from "../../api";
import PerseusDictionarySense from "./PerseusDictionarySense.vue";

const debounce = require("lodash.debounce");

const GREEK_DICTIONARIES = [
  "anabasis-mather",
  "cunliffe-hompers",
  "cunliffe-lex-entries",
  "lexicon-thucydideum",
  "lsj",
  "middle-liddel",
  "short-defs",
  "slater-pindar",
];

const LATIN_DICTIONARIES = [
  "elementary-latin",
  "latin-short-defs",
  "lewis-and-short-latin-dictionary",
  "short-defs",
];

const OTHER_DICTIONARIES = ["brunetti-short-defs-for-beowulf"];

export default {
  name: "widget-perseus-dictionary",
  components: {
    PerseusDictionarySense,
  },
  computed: {
    availableDictionaries() {
      const urn = this.$store.state.reader.leftPassage.urn.value;

      if (urn.includes("-grc")) {
        return this.$store.state.reader.availableDictionaries.filter((d) =>
          GREEK_DICTIONARIES.includes(d.slug),
        );
      } else if (urn.includes("-lat")) {
        return this.$store.state.reader.availableDictionaries.filter((d) =>
          LATIN_DICTIONARIES.includes(d.slug),
        );
      }

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
    dictionaryQuery() {
      return this.$store.state.reader.dictionaryQuery;
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
      dictionary = "lewis-and-short-latin-dictionary";
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
      this.loading = true;

      api.searchPerseusDictionary(
        this.selectedDictionary,
        { q: this.query },
        ({ current_page, results, total_pages }) => {
          this.results = results;
          this.currentPage = current_page;
          this.totalPages = total_pages;

          this.loading = false;
        },
      );
    }, 250),
  },

  watch: {
    dictionaryQuery(newVal) {
      this.q = newVal;
    },
    selectedDictionary: "updateSearch",
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

.loading-container {
  --uib-size: 43px;
  --uib-color: black;
  --uib-speed: 1.3s;
  --uib-dot-size: calc(var(--uib-size) * 0.24);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--uib-dot-size);
  width: var(--uib-size);
}

.dot,
.loading-container::before,
.loading-container::after {
  content: "";
  display: block;
  height: var(--uib-dot-size);
  width: var(--uib-dot-size);
  border-radius: 50%;
  background-color: var(--uib-color);
  transform: scale(0);
  transition: background-color 0.3s ease;
}

.loading-container::before {
  animation: pulse var(--uib-speed) ease-in-out calc(var(--uib-speed) * -0.375)
    infinite;
}

.dot {
  animation: pulse var(--uib-speed) ease-in-out calc(var(--uib-speed) * -0.25)
    infinite both;
}

.loading-container::after {
  animation: pulse var(--uib-speed) ease-in-out calc(var(--uib-speed) * -0.125)
    infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(0);
  }

  50% {
    transform: scale(1);
  }
}
</style>
