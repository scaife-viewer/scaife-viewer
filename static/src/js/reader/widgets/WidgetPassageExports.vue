<template>
  <base-widget class="passage-exports">
    <span slot="header">Export Passage</span>
    <div slot="body">
      <template v-if="rightPassage">
        <p>
          <span class="side">L</span>
          <span class="links">
            as
            <a :href="getPassageUrl(leftPassage, 'text')">text</a>
            or
            <a :href="getPassageUrl(leftPassage, 'xml')">xml</a>
          </span>
        </p>
        <p>
          <span class="side">R</span>
          <span class="links">
            as
            <a :href="getPassageUrl(rightPassage, 'text')">text</a>
            or
            <a :href="getPassageUrl(rightPassage, 'xml')">xml</a>
          </span>
        </p>
      </template>
      <template v-else>
        <p>
          <span class="links">
            as
            <a :href="getPassageUrl(passage, 'text')">text</a>
            or
            <a :href="getPassageUrl(passage, 'xml')">xml</a>
          </span>
        </p>
      </template>
    </div>
  </base-widget>
</template>

<script>
const baseURL = `${process.env.FORCE_SCRIPT_NAME}` || "";

export default {
  name: "widget-passage-exports",
  methods: {
    getPassageUrl(passage, format) {
      return `${baseURL}/library/passage/${passage.urn.toString()}/${format}/`;
    },
  },
  computed: {
    passage() {
      return this.$store.getters["reader/passage"];
    },
    leftPassage() {
      return this.$store.state.reader.leftPassage;
    },
    rightPassage() {
      return this.$store.state.reader.rightPassage;
    }
  }
};
</script>
