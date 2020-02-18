<script>
// This component has a render() method instead of a <template> section because
// it is being loaded at runtime rather than pre-compiled.
import constants from '../constants';

export default {
  name: 'inline-token',
  props: {
    t: { type: String, required: true, },
    w: { type: String, required: true, },
    i: { type: String, required: true, },
  },
  inject: ['highlighting'],
  computed: {
    idx() {
      return `${this.w}[${this.i}]`;
    },
  },
  methods: {
    processTokenClick(evt, clickable, selected, idx) {
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
    }
  },
  render(h) {
    let selected = false;
    let highlighted = false;
    let clickable = false;
    const vueInstance = this;
    const {
      t, idx, highlighting,
      $parent: p,
      $store: store,
    } = this;
    const { visible } = p;
    if (visible && highlighting) {
      const { textMode, annotations, annotationChange } = store.state.reader;
      if (textMode === 'clickable') {
        clickable = true;
      }
      if (annotations.has(idx)) {
        ({ selected, highlighted } = annotations.get(idx));
      }
    }
    return h(
      'span',
      {
        class: [
          t,
          { c: clickable, selected, highlighted },
        ],
        on: {
          click(e) {
            if (clickable) {
              vueInstance.processTokenClick(e, clickable, selected, idx);
            }
          },
        },
      },
      this.$slots.default,
    );
  },
};
</script>
