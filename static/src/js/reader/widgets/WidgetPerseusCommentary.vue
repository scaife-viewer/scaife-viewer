<template>
  <base-widget class="perseus-commentary">
    <span slot="header">Perseus Commentary</span>
    <div slot="body">
      <div>
        <div
          v-for="entry in commentaryEntries"
          :key="entry.idx"
          :id="entry.urn"
          :corresp="entry.corresp"
        >
          <span>{{ entry.corresp.split(":").at(-1) }}. </span>
          <div v-html="entry.content" />
        </div>
      </div>
    </div>
  </base-widget>
</template>

<script>
export default {
  name: "widget-perseus-commentary",
  computed: {
    commentaryEntries() {
      return this.$store.state.reader.commentaryEntries;
    },
  },
};
</script>

<style>
lem {
  font-weight: bold;
}
</style>
