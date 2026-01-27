<template>
  <div class="repo-metadata-widget">
    <RepoMetadata :passage="passage" />
  </div>
</template>

<script>
// NOTE: (pletcher) This widget was originally provided by an external package at
// https://github.com/scaife-viewer/frontend/blob/main/packages/widget-repo-metadata/src/RepoMetadataWidget.vue
// These packages are no longer being served correctly, so
// I'm inlining them here.
import { MODULE_NS } from "@scaife-viewer/store";
import RepoMetadata from "./RepoMetadata.vue";

/**
 * Widget used to display information / link to
 * the source repository for a given text.
 */
export default {
  name: "RepoMetadataWidget",
  components: {
    RepoMetadata,
  },
  scaifeConfig: {
    displayName: "Repository",
  },
  computed: {
    passage() {
      return this.$store.getters[`${MODULE_NS}/passage`];
    },
  },
};
</script>

<style lang="scss" scoped>
.repo-metadata-widget {
  justify-content: flex-start;
  width: 100%;
}
</style>
