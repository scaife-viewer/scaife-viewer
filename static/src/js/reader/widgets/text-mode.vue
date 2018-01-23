<template>
  <widget class="text-mode">
    <span slot="header">Text Mode</span>
    <div slot="body">
      <a :class="['mode', {active: textMode === 'browser'}]" @click.prevent="changeTextMode('browser')">Browser</a>
      <a :class="['mode', {active: textMode === 'clickable'}]" @click.prevent="changeTextMode('clickable')">Clickable</a>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget';

export default {
  store,
  computed: {
    textMode() {
      return this.$store.state.reader.textMode;
    },
  },
  methods: {
    changeTextMode(mode) {
      this.$store.dispatch('reader/setSelectedToken', { token: null })
        .then(() => {
          this.$store.commit('reader/setTextMode', { mode });
        });
    },
  },
  components: {
    widget,
  },
};
</script>
