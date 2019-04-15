<template>
  <base-widget class="passage-links">
    <span slot="header">CTS URN</span>
    <div slot="body">
      <template v-if="rightPassage">
        <p v-if="ctsApiUrl"><span class="side">L</span> <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${leftPassage.urn}`">{{ leftPassage.urn.toString() }}</a></tt></p>
        <p v-else><span class="side">L</span> <tt>{{ leftPassage.urn.toString() }}</tt></p>
        <p v-if="ctsApiUrl"><span class="side">R</span> <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${rightPassage.urn}`">{{ rightPassage.urn.toString() }}</a></tt></p>
        <p v-else><span class="side">R</span> <tt>{{ rightPassage.urn.toString() }}</tt></p>
      </template>
      <template v-else>
        <p v-if="ctsApiUrl"><tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${passage.urn}`">{{ passage.urn.toString() }}</a></tt></p>
        <p v-else><tt>{{ passage.urn.toString() }}</tt></p>
      </template>
    </div>
  </base-widget>
</template>

<script>
export default {
  name: 'widget-passage-links',
  computed: {
    ctsApiUrl() {
      return process.env.CTS_API_ENDPOINT
    },
    passage() {
      return this.$store.getters['reader/passage'];
    },
    leftPassage() {
      return this.$store.state.reader.leftPassage;
    },
    rightPassage() {
      return this.$store.state.reader.rightPassage;
    },
  },
};
</script>
