<template>
  <base-widget class="perseus-commentary">
    <span slot="header">Perseus Dictionary</span>
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
// TODO: Consult larger dictionary than Word List
// Rename "Word List" to "Glossary"
// Do a search
// Open a widget with a default dictionary and options
// for other dictionaries
// Sort dictionaries by size: for Homer, start with Cunliffe
// Dictionaries have lists of relevant URN fragments
// Default to LSJ or Lewis and Short
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
