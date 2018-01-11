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
  computed: {
    idx() {
      return `${this.w}[${this.i}]`;
    },
  },
  render(h) {
    let selected = false;
    const {
      t, idx,
      $parent: p,
      $store: store,
    } = this;
    const { visible } = p;
    if (visible) {
      const { annotations, annotationChange } = store.state.reader;
      if (annotations.has(idx)) {
        ({ selected } = annotations.get(idx));
      }
    }
    return h(
      'span',
      {
        class: [
          t,
          { selected },
        ],
        on: {
          click(e) {
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
          },
        },
      },
      this.$slots.default,
    );
  },
};
</script>
