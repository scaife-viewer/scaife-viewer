<template>
  <div class="widget">
    <h2>Word List</h2>
    <div v-for="word in wordList" :key="word.text">
      <b>{{ word.text }}</b><br />
      <small>{{ word.shortdef }}</small>
    </div>
  </div>
</template>

<script>
import store from '../../store';

export default {
  store,
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
  data() {
    return {
      wordList: [],
    };
  },
  mounted() {
    this.fetchWordList();
  },
  watch: {
    passage: 'fetchWordList',
  },
  methods: {
    async fetchWordList() {
      const server = 'https://gu658.us1.eldarioncloud.com';
      const { urn } = this.passage;
      const res = await fetch(`${server}/word-list/${urn}/json/?page=all`);
      if (!res.ok) {
        throw new Error(res.status);
      }
      const data = await res.json();
      this.wordList = data.lemmas.map(lemma => ({
        text: lemma.lemma_text,
        shortdef: lemma.shortdef,
      }));
    },
  },
};
</script>
