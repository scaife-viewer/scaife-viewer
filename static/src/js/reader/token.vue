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
  render(h) {
    let selected = false;
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
        ({ selected } = annotations.get(idx));
      }
    }
    return h(
      'span',
      {
        class: [
          t,
          { c: clickable, selected },
        ],
        on: {
          click(e) {
            if (clickable) {
              if (e.metaKey) {
                if (selected) {
                  store.dispatch('reader/setSelectedToken', { token: null });
                }
              } else if (e.shiftKey) {
                store.dispatch('reader/selectTokenRange', { token: idx });
              } else {
                store.dispatch('reader/setSelectedToken', { token: idx });
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
