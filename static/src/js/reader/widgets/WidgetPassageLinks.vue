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
export default {
  name: 'WidgetPassageLinks',
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
      const baseURL = this.$router.options.base;
      return `${baseURL}library/${urn}/cts-api-xml/`;
    },
  },
};
</script>
