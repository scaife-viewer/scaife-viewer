<template>
  <widget class="morpheus">
    <span slot="header">Morpheus</span>
    <div slot="body" v-if="morphBody">
      <pre>{{ morphBody }}</pre>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget';

export default {
  store,
  watch: {
    selectedWord: 'fetchData',
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
            this.morphBody = data.RDF.Annotation.Body;
          });
        });
      } else {
        this.morphBody = null;
      }
    },
  },
  components: {
    widget,
  },
};
</script>
