<script>
// This component has a render() method instead of a <template> section because
// it is being loaded at runtime rather than pre-compiled.
import constants from '../constants';

export default {
  name: 'InlineToken',
  props: {
    t: { type: String, required: true },
    w: { type: String, required: true },
    i: { type: String, required: true },
    veRef: { type: String, required: false },
  },
  inject: ['highlighting'],
  computed: {
    idx() {
      return `${this.w}[${this.i}]`;
    },
  },
  methods: {
    processTokenClick(evt, selected, idx) {
      if (evt.metaKey && selected) {
        // clear input
        this.$store.dispatch(`reader/${constants.READER_SET_SELECTED_TOKEN}`, { token: null });
      } else if (evt.shiftKey) {
        // add to selection
        this.$store.dispatch(`reader/${constants.READER_SELECT_TOKEN_RANGE}`, { token: idx });
      } else {
        // set selection
        this.$store.dispatch(`reader/${constants.READER_SET_SELECTED_TOKEN}`, { token: idx });
      }
      evt.stopPropagation();
    },
  },
  // TODO: Consider computed props for more consistency
  render(h) {
    let selected = false;
    let highlighted = false;
    let clickable = false;
    let hasCommentary = false;
    const vueInstance = this;
    const {
      t, idx, highlighting, veRef,
      $parent: p,
      $store: store,
    } = this;
    const { visible } = p;
    if (visible && highlighting) {
      // TODO: Determine why annotationChange is required for reactivity;
      // likely this is due to annotations being a Map
      const {
        textMode, annotations, annotationChange, commentaryTokensHash,
      } = store.state.reader;
      if (textMode === 'clickable') {
        clickable = true;
      }
      if (annotations.has(idx)) {
        ({ selected, highlighted } = annotations.get(idx));
      }
      hasCommentary = commentaryTokensHash[veRef];
    }
    return h(
      'span',
      {
        class: [
          t,
          {
            c: clickable, selected, highlighted, commentary: hasCommentary,
          },
        ],
        attrs: {
          title: veRef,
        },
        on: {
          click(e) {
            if (clickable) {
              vueInstance.processTokenClick(e, selected, idx);
            }
          },
        },
      },
      this.$slots.default,
    );
  },
};
</script>
