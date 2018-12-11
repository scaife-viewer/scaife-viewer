<script>
export default {
  name: 'Token',
  props: {
    t: {
      type: String,
      required: true,
    },
    w: {
      type: String,
      required: true,
    },
    i: {
      type: String,
      required: true,
    },
  },
  inject: ['highlighting'],
  computed: {
    idx() {
      return `${this.w}[${this.i}]`;
    },
  },
  methods: {
    readerDispatch(action, params) {
      this.$store.dispatch(`reader/${action}`, params);
    }
  },
  render(h) {
    let selected = false;
    let highlighted = false;
    let clickable = false;
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
              if (e.metaKey) {
                if (selected) {
                  this.readerDispatch(constants.READER_SET_SELECTED_TOKEN, { token: null });
                }
              } else if (e.shiftKey) {
                this.readerDispatch(constants.READER_SELECT_TOKEN_RANGE, { token: idx });
              } else {
                this.readerDispatch(constants.READER_SET_SELECTED_TOKEN, { token: idx });
              }
              e.stopPropagation();
            }
          },
        },
      },
      this.$slots.default,
    );
  },
};
</script>
