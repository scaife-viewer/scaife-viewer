<template>
  <base-widget class="morpheus" v-if="enabled">
    <span slot="header">Morphology</span>
    <div slot="body">
      <text-loader v-if="loading" size="7px" margin="1px" />
      <div v-else-if="morphBody">
        <div class="group" v-for="group in morphBody" :key="group.uri">
          <div class="head">
            <span class="hdwd" @click="searchDictionary(group.hdwd)" style="cursor: pointer;">{{ group.hdwd }}</span>
            <span class="pofs-decl">{{ group.pofs }} {{ group.decl }}</span>
          </div>
          <div v-if="shortDef(group.hdwd)" class="shortdef">{{ shortDef(group.hdwd) }}</div>
          <div class="entries">
            <div class="entry" v-for="entry in group.infl">
              <div class="form">
                <span class="stem">{{ entry.stem }}</span><span v-if="entry.suff" class="suff">-{{ entry.suff }}</span>
              </div>
              <!-- {{ entry.pofs }} -->
              <!-- {{ entry.stemtype }} -->
              <div class="props">
                {{ entry.tense }}
                {{ entry.voice }}
                {{ entry.mood }}
                {{ entry.pers }}
                {{ entry.case }}
                {{ entry.num }}
                {{ entry.gend }}
                {{ entry.comp }}
                <span v-if="entry.dial" class="dial">({{ entry.dial }})</span>
              </div>
              <!-- {{ entry.derivtype }} -->
              <!-- {{ entry.morph }} -->
            </div>
          </div>
        </div>
      </div>
      <p v-else-if="selectedWord" class="no-results">No results found.</p>
      <p v-else class="instructions">In <span class="mode">HIGHLIGHT</span> text mode, select a word to get morphological analysis (Greek and Latin only).</p>
    </div>
  </base-widget>
</template>

<script>
import constants from '../../constants';
import TextLoader from '../../components/TextLoader.vue';

export default {
  name: 'widget-morpheus',
  watch: {
    selectedWord: {
      handler: 'fetchData',
      immediate: true,
    },
  },
  data() {
    return {
      loading: false,
      morphBody: null,
    };
  },
  computed: {
    enabled() {
      return this.text.metadata.lang === 'grc' || this.text.metadata.lang === 'lat';
    },
    selectedWords2() {
      return this.$store.getters['reader/selectedWords2'];
    },
    selectedWords() {
      return this.$store.getters['reader/selectedWords'];
    },
    selectedWord() {
      if (this.selectedWords2.length === 0) {
        return null;
      }
      return this.selectedWords2[0];
    },
    text() {
      const text = this.$store.getters['reader/text'];
      return text;
    },
    wordList() {
      return this.$store.state.reader.wordList;
    },
  },
  methods: {
    shortDef(hdwd) {
      const entry = this.wordList.find(w => w.text === hdwd);
      return entry ? entry.shortdef : null;
    },
    fetchData() {
      const word = this.selectedWord;
      const lang = this.text.metadata.lang;
      if (word) {
        this.loading = true;
        const baseURL = this.$router.options.base;
        const url = `${baseURL}morpheus/?word=${word.w}&lang=${lang}`;
        const headers = new Headers({
          Accept: 'application/json',
        });
        fetch(url, { method: 'GET', headers }).then((resp) => {
          resp.json().then((data) => {
            if (data.Body && data.Body.length > 0) {
              this.morphBody = data.Body;
              const lemmas = [];
              this.morphBody.forEach(({ hdwd }) => {
                lemmas.push(hdwd);
              });
              this.$store.commit(`reader/${constants.READER_SET_SELECTED_LEMMAS}`, { lemmas });
              this.$store.commit(`reader/${constants.READER_SET_DICTIONARY_QUERY}`, { query: this.morphBody[0].hdwd });
            } else {
              this.reset();
            }
            this.loading = false;
          });
        });
      } else {
        this.reset();
      }
    },
    searchDictionary(hdwd) {
      this.$store.commit(`reader/${constants.READER_SET_DICTIONARY_QUERY}`, { query: hdwd });
    },
    reset() {
      this.morphBody = null;
      this.$store.commit(`reader/${constants.READER_SET_SELECTED_LEMMAS}`, { lemmas: null });
      this.$store.commit(`reader/${constants.READER_SET_DICTIONARY_QUERY}`, { query: '' });
    },
  },
  components: {
    TextLoader,
  },
};
</script>
