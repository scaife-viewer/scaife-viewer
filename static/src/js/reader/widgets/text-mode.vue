<template>
  <widget class="text-mode">
    <span slot="header">Text Mode</span>
    <div slot="body">
      <div class="mode">
        <a :class="[{active: textMode === 'browser'}]" @click.prevent="changeTextMode('browser')">normal</a>
        <a :class="[{active: textMode === 'clickable'}]" @click.prevent="changeTextMode('clickable')">highlight</a>
      </div>
      <div class="help">
        <span v-if="textMode === 'browser'">normal selection of text for copying possible</span>
        <span v-if="textMode === 'clickable'">click and shift-click on words to highlight</span>
      </div>
    </div>
  </widget>
</template>

<script>
import widget from '../widget.vue';

export default {
  computed: {
    textMode() {
      return this.$store.state.reader.textMode;
    },
  },
  methods: {
    changeTextMode(mode) {
      this.$store.dispatch(`reader/${constants.READER_SET_SELECTED_TOKEN}`, { token: null })
        .then(() => {
          this.$store.commit(constants.SET_TEXT_MODE, { mode });
        });
    },
  },
  components: {
    widget,
  },
};
</script>
