<template>
  <base-widget class="passage-links">
    <span slot="header">CTS URN</span>
    <div slot="body">
      <template v-if="rightPassage">
        <p><span class="side">L</span> <tt><a :href="getPassageUrl(leftPassage.urn)">{{ leftPassage.urn.toString() }}</a></tt></p>
        <p><span class="side">R</span> <tt><a :href="getPassageUrl(rightPassage.urn)">{{ rightPassage.urn.toString() }}</a></tt></p>
      </template>
      <template v-else>
        <p><tt><a :href="getPassageUrl(passage.urn)">{{ passage.urn.toString() }}</a></tt></p>
      </template>
    </div>
  </base-widget>
</template>

<script>
// TODO: Grab this from $router
const baseURL = `${process.env.FORCE_SCRIPT_NAME}` || "";

export default {
  name: 'widget-passage-links',
  computed: {
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
  methods: {
    getPassageUrl(urn) {
      return `${baseURL}/library/passage/${urn}/cts-api-xml/`;
    },
  },
};
</script>
