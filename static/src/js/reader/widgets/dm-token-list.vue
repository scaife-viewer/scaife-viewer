<template>
  <widget class="token-list" v-if="enabled && show">
    <span slot="header">Token List</span>
    <div slot="body">
      <table>
        <template v-for="token in tokenList">
          <tr v-for="(analysis, idx) in token.analyses">
            <th class="text"><template v-if="idx === 0">{{ token.text }}</template></th>
            <td class="parse">{{ analysis.parse }}</td>
            <td class="text">{{ analysis.lemma }}</td>
          </tr>
        </template>
      </table>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import { URN } from '../../scaife-viewer';
import widget from '../widget';

export default {
  store,
  computed: {
    text() {
      return this.$store.getters['reader/text'];
    },
    passage() {
      return this.$store.getters['reader/passage'];
    },
    enabled() {
      const urn = new URN(this.text.urn);
      return this.text.metadata.lang === 'grc' && urn.upTo('textGroup') === 'urn:cts:greekLit:tlg0012';
    },
  },
  data() {
    return {
      show: false,
      tokenList: [],
    };
  },
  watch: {
    passage: 'fetchTokenList',
  },
  created() {
    if (this.enabled) {
      this.fetchTokenList();
    }
  },
  methods: {
    async fetchTokenList() {
      const server = 'https://morph.perseus.org';
      const { urn } = this.passage;
      const res = await fetch(`${server}/read/${urn}/json/`);
      if (!res.ok) {
        if (res.status === 404) {
          this.show = false;
          return;
        }
        throw new Error(res.status);
      }
      if (this.show === false) {
        this.show = true;
      }
      const data = await res.json();
      this.tokenList = data.tokens;
    },
  },
  components: {
    widget,
  },
};
</script>
