<template>
  <base-widget class="highlight">
    <span slot="header">Highlight</span>
    <div slot="body">
      <input
        v-model="value"
        v-on:keyup="handleKeyUp"
        v-on:click="handleClick"
        type="text"
        class="form-control form-control-sm"
      >
    </div>
  </base-widget>
</template>

<script>
import constants from '../../constants';

export default {
  name: 'widget-highlight',
  watch: {
    highlight: 'setInputVal',
  },
  mounted() {
    this.setInputVal();
    const queryParams = this.$route.query;
    if (Object.entries(queryParams).length !== 0 && queryParams.constructor === Object) {
      if (queryParams.highlight) {
        this.$store.dispatch(`reader/${constants.READER_HIGHLIGHT}`, { highlight: queryParams.highlight });
      }
    }
  },
  computed: {
    highlight() {
      return this.$store.state.reader.highlight;
    },
  },
  data() {
    return {
      value: '',
    };
  },
  methods: {
    setInputVal() {
      this.value = this.highlight;
      this.updateHighlightQueryParam();
    },
    updateHighlightQueryParam() {
      /*
        Since the `highlight` computed property is reactive, when
        `$store.state.reader.highlight` is changed, the widget will
        update the `highlight` query param
      */
      this.$router.replace({
        query: {
          highlight: this.value,
        },
      });
    },
    handleKeyUp(e) {
      if (e.keyCode === 13) {
        if (this.value === '') {
          this.$store.dispatch(`reader/${constants.READER_HIGHLIGHT}`, { highlight: null });
        } else {
          this.$store.dispatch(`reader/${constants.READER_HIGHLIGHT}`, { highlight: this.value });
        }
        e.currentTarget.blur();
      } else {
        e.stopPropagation();
      }
    },
    handleClick(e) {
      const el = e.currentTarget;
      el.select();
    },
  },
};
</script>
