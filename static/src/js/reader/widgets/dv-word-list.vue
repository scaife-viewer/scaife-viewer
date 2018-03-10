<template>
  <widget class="word-list" v-if="show">
    <span slot="header">Word List</span>
    <div slot="sticky">
      <p v-if="!usedFallbackApi" class="legend">Number in parentheses is frequency per 10k in this work.</p>
    </div>
    <div slot="body">
      <p v-for="word in wordList" :key="word.text" v-if="!selectedLemmas || selectedLemmas.indexOf(word.text) !== -1">
        <span class="w">{{ word.text }}</span>
        <span class="df">{{ word.shortdef }}</span>
        <span v-if="word.frequency" class="fr">({{ word.frequency }})</span>
      </p>
    </div>
  </widget>
</template>

<script>
import qs from 'query-string';
import store from '../../store';
import widget from '../widget';

export default {
  store,
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
    selectedLemmas() {
      return this.$store.state.reader.selectedLemmas;
    },
  },
  data() {
    return {
      show: false,
      usedFallbackApi: false,
      wordList: [],
    };
  },
  watch: {
    passage: {
      handler: 'fetchWordList',
      immediate: true,
    },
    selectedLemmas: 'fetchWordList',
  },
  methods: {
    async fetchWordList() {
      const server = 'https://gu658.us1.eldarioncloud.com';
      const { urn } = this.passage;
      let res = await fetch(`${server}/word-list/${urn}/json/?page=all&amp;o=1`);
      if (!res.ok) {
        if (res.status === 404) {
          if (this.selectedLemmas && this.selectedLemmas.length > 0) {
            const params = qs.stringify({ l: this.selectedLemmas });
            res = await fetch(`${server}/lemma/json/?${params}`);
            if (!res.ok) {
              throw new Error(res.status);
            }
            const data = await res.json();
            this.wordList = data.lemmas;
            this.usedFallbackApi = true;
            this.show = true;
          } else {
            this.show = false;
          }
          return;
        }
        throw new Error(res.status);
      }
      if (this.show === false) {
        this.show = true;
      }
      const data = await res.json();
      this.wordList = data.lemmas.map(lemma => ({
        text: lemma.lemma_text,
        shortdef: lemma.shortdef,
        frequency: lemma.work_frequency.toFixed(2),
      }));
    },
  },
  components: {
    widget,
  },
};
</script>
