<template>
  <base-widget v-if="shown">
    <span
      slot="header"
    >
      Dictionary Entries
    </span>
    <PortalTarget
      slot="sticky"
      :name="'dictionary-entries-widget-controls'"
    />
    <div slot="body">
      <DictionaryEntriesWidget />
    </div>
  </base-widget>
</template>

<script>
import { PortalTarget } from 'portal-vue';
import DictionaryEntriesWidget from '@scaife-viewer/widget-dictionary-entries';

export default {
  name: 'WidgetDictionaryEntries',
  components: {
    PortalTarget,
    DictionaryEntriesWidget,
  },
  computed: {
    portalTarget() {
      return 'dictionary-entries-widget-controls'
    },
    passage() {
      return this.$store.getters['reader/passage'];
    },
    shown() {
      // TODO: Implement widget contract within SV 2;
      // until then, we will need to add to this conditional
      // to support additional dictionaries.
      return this.passage ? this.passage.urn.textGroup === 'tlg0003' : false;
    },
  },
};
</script>

<style lang="scss">
  // TODO: Remove widget customizations when using SV 2 Skeleton
  .dictionary-entries-widget {
    margin: 0;
    padding: 0 8px;
  }
  .controls {
    margin: 0 !important;
    width: 100% !important;
    padding: 0 8px;
  }
</style>
