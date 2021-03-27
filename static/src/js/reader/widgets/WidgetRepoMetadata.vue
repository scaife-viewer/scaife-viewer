<template>
  <base-widget>
    <span slot="header">Repository</span>
    <div slot="body">
      <repo-metadata-widget />
    </div>
  </base-widget>
</template>

<script>
import RepoMetadataWidget from '@scaife-viewer/widget-repo-metadata';

export default {
  name: 'WidgetRepoMetadata',
  components: {
    RepoMetadataWidget,
  },
};
</script>
