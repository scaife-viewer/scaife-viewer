<template>
  <base-widget class="perseus-commentary">
    <span slot="header">Perseus Commentary</span>
    <div slot="body">
      <div
        v-for="entry in commentaryEntries"
        :key="entry.idx"
        :id="entry.urn"
        :corresp="entry.corresp"
      >
        <span class="commentary-entry-citation">{{ entry.corresp.split(":").at(-1).replace("_", "-") }}.</span>
        <div class="commentary-entry-content" v-html="entry.content" />
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

.commentary-entry-citation {
  display: inline-block;
  float: left;
}


.commentary-entry-content {
  text-indent: 2ch;
}
</style>
