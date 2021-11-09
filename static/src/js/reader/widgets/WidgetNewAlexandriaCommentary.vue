<template>
  <base-widget class="new-alexandria-commentary" v-if="show">
    <span slot="header">New Alexandria Commentary</span>
    <div slot="body">
      <new-alexandria-widget />
    </div>
  </base-widget>
</template>

<script>
import NewAlexandriaWidget from '@scaife-viewer/widget-new-alexandria';

export default {
  name: 'widget-attributions',
  components: {
    NewAlexandriaWidget,
  },
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
    show() {
      // TODO: Restore the previous functionality where we used a 404
      // from the server to determine if the widget was shown or not.
      return this.$store.getters['reader/passage'].urn.textGroup === 'tlg0012'
    },
  },
};
</script>
<style lang="scss">
.new-alexandria-commentary {
  img {
    max-width: 100%;
  }
}
</style>

