<template>
  <div class="widget token-list" v-if="show">
    <h2>Token List</h2>
    <table class="table table-sm table-striped">
      <template v-for="token in tokenList">
        <tr v-for="(analysis, idx) in token.analyses">
          <th><template v-if="idx === 0">{{ token.text }}</template></th>
          <td>{{ analysis.parse }}</td>
          <td>{{ analysis.lemma }}</td>
        </tr>
      </template>
    </table>
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
      show: false,
      tokenList: [],
    };
  },
  mounted() {
    this.fetchTokenList();
  },
  watch: {
    passage: 'fetchTokenList',
  },
  methods: {
    async fetchTokenList() {
      const server = 'https://li550.us1.eldarioncloud.com';
      const { urn } = this.passage;
      const res = await fetch(`${server}/read/${urn}/json/`);
      if (!res.ok) {
        if (res.status === 404) {
          this.show = false;
        } else {
          throw new Error(res.status);
        }
      }
      if (this.show === false) {
        this.show = true;
      }
      const data = await res.json();
      this.tokenList = data.tokens;
    },
  },
};
</script>
