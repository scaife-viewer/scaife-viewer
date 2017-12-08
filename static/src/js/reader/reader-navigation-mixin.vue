<script>
import store from '../store';
import { URN } from '../scaife-viewer';

export default {
  store,
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
        query: this.$store.state.route.query,
      };
    },
    toRightPassage(urn) {
      if (!(urn instanceof URN)) {
        urn = new URN(urn);
      }
      return {
        name: 'reader',
        params: this.$store.state.route.params,
        query: { right: urn.version },
      };
    },
    toRef(reference) {
      const passage = this.$store.getters['reader/passage'];
      const urn = passage.urn.replace({ reference });
      return {
        name: 'reader',
        params: { leftUrn: urn.toString() },
        query: this.$store.state.route.query,
      };
    },
    toRemoveLeft() {
      const { urn } = this.$store.state.reader.rightPassage;
      return { name: 'reader', params: { leftUrn: urn.toString() } };
    },
    toRemoveRight() {
      const { urn } = this.$store.state.reader.leftPassage;
      return { name: 'reader', params: { leftUrn: urn.toString() } };
    },
  },
};
</script>
