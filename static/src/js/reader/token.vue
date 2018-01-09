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
    r: {
      type: String,
      required: false,
    },
  },
  render(h) {
    let selected = false;
    const {
      r, t, w, i,
      $parent: p,
      $store: store,
    } = this;
    const { visible } = p;
    if (r && visible) {
      const { highlight } = store.state.reader;
      if (highlight) {
        const [, aw, ai] = /^@([^[]+)(?:\[(\d+)\])?$/.exec(highlight);
        selected = (aw === w && ai === i);
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
                store.dispatch('reader/highlight', { highlight: null });
              }
            } else if (t === 'w') {
              store.dispatch('reader/highlight', { highlight: `@${w}[${i}]` });
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
