<script>
import URN from '../urn';

export default {
  methods: {
    toPassage(urn) {
      if (!(urn instanceof URN)) {
        urn = new URN(urn);
      }
      const passage = this.$store.getters['reader/passage'];
      // urn can be either a text URN with or without a reference.
      // if no reference is given use the existing reference.
      if (!urn.reference) {
        urn = urn.replace({ reference: passage.urn.reference });
      }
      return {
        name: 'reader',
        params: { leftUrn: urn.toString() },
        query: this.$route.query,
      };
    },
    toRightPassage(urn) {
      if (!(urn instanceof URN)) {
        urn = new URN(urn);
      }
      return {
        name: 'reader',
        params: this.$route.params,
        query: { ...this.$route.query, right: urn.version },
      };
    },
    toLowerPassage(urn) {
      if (!(urn instanceof URN)) {
        urn = new URN(urn);
      }
      var x = {
        name: 'reader',
        params: this.$route.params,
        query: { ...this.$route.query, lower: urn.toString() },
      };
      return x;
    },
    toRef(reference) {
      const passage = this.$store.getters['reader/passage'];
      const urn = passage.urn.replace({ reference });
      return {
        name: 'reader',
        params: { leftUrn: urn.toString() },
        query: this.$route.query,
      };
    },
    toRemoveLeft() {
      const { urn } = this.$store.state.reader.rightPassage;
      return {
        name: 'reader',
        params: { leftUrn: urn.toString() },
        query: (({ right: deleted, ...o }) => o)(this.$route.query),
      };
    },
    toRemoveRight() {
      const { urn } = this.$store.state.reader.leftPassage;
      return {
        name: 'reader',
        params: { leftUrn: urn.toString() },
        query: (({ right: deleted, ...o }) => o)(this.$route.query),
      };
    },
    toRemoveLower() {
      const { urn } = this.$store.state.reader.leftPassage;
      return {
        name: 'reader',
        params: { leftUrn: urn.toString() },
        query: (({ lower: deleted, ...o }) => o)(this.$route.query),
      };
    },
  },
};
</script>
