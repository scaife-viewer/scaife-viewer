<template>
  <div class="attributions-widget">
    <Attributions :version-urn="versionUrn" />
  </div>
</template>

<script>
// NOTE: (pletcher) This widget was originally provided by an external package at
// https://github.com/scaife-viewer/frontend/blob/main/packages/widget-attributions/src/AttributionsWidget.vue
// These packages are no longer being served correctly, so
// I'm inlining them here.
// TODO: Determine other patterns for this type of widget;
// e.g., when do we have a widget wrapping another component
// Can we also re-use / inherit from metadata styles?
import { MODULE_NS } from "@scaife-viewer/store";
import Attributions from "./Attributions.vue";

export default {
  name: "AttributionsWidget",
  components: {
    Attributions,
  },
  scaifeConfig: {
    displayName: "Attributions",
  },
  computed: {
    passage() {
      return this.$store.getters[`${MODULE_NS}/passage`];
    },
    versionUrn() {
      return this.passage.version;
    },
  },
};
</script>

<style lang="scss" scoped>
.attributions-widget {
  justify-content: flex-start;
  width: 100%;
}
</style>
