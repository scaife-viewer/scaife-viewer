<template>
  <widget class="morpheus">
    <span slot="header">Morpheus</span>
    <div slot="body">
      <div v-if="morphBody">
        <div class="group" v-for="group in morphBody" :key="group.uri">
          <div class="head">
            <span class="hdwd">{{ group.hdwd }}</span>
            <span class="pofs-decl">{{ group.pofs }} {{ group.decl }}</span>
          </div>
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
      <p v-else class="instructions">In <span class="mode">HIGHLIGHT</span> text mode, select a word to get morphological analysis (Greek only).</p>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget';

export default {
  store,
  watch: {
    selectedWord: {
      handler: 'fetchData',
      immediate: true,
    },
  },
  data() {
    return {
      morphBody: null,
    };
  },
  computed: {
    selectedWord() {
      const selectedWords = this.$store.getters['reader/selectedWords'];
      if (selectedWords.length === 0) {
        return null;
      }
      return selectedWords[0];
    },
  },
  methods: {
    fetchData() {
      const word = this.selectedWord;
      if (word) {
        const url = `/morpheus/?word=${word.w}`;
        const headers = new Headers({
          Accept: 'application/json',
        });
        fetch(url, { method: 'GET', headers }).then((resp) => {
          resp.json().then((data) => {
            this.morphBody = data.Body;
            const lemmas = [];
            this.morphBody.forEach(({ hdwd }) => {
              lemmas.push(hdwd);
            });
            this.$store.commit('reader/setSelectedLemmas', { lemmas });
          });
        });
      } else {
        this.morphBody = null;
        this.$store.commit('reader/setSelectedLemmas', { lemmas: null });
      }
    },
  },
  components: {
    widget,
  },
};
</script>
