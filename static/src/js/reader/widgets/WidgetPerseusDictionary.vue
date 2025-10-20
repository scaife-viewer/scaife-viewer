<template>
  <base-widget class="perseus-dictionary">
    <span slot="header">Perseus Dictionaries</span>
    <div slot="body">
      <div>
        <div
          v-for="dictionary in availableDictionaries"
          :key="dictionary.urn"
          :id="dictionary.urn"
        >
          <span>{{ dictionary.label }} </span>
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
  name: "widget-perseus-dictionary",
  computed: {
    availableDictionaries() {
      return this.$store.state.reader.availableDictionaries;
    },
  },
};
</script>

<style>
lem {
  font-weight: bold;
}
</style>
