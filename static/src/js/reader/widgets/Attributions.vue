<template>
  <div class="attributions-container">
    <!-- TODO: handle empty scenarios -->
    <div
      :key="roleGroup[0]"
      class="attribution-row"
      v-for="roleGroup in attributionsByRole"
    >
      <div class="label">{{ roleGroup[0] }}</div>
      <div
        :key="attribution.id"
        v-for="attribution in roleGroup[1]"
        class="value"
      >
        {{ attribution.name }}
      </div>
    </div>
  </div>
</template>

<script>
// NOTE: (pletcher) This widget was originally provided by an external package at
// https://github.com/scaife-viewer/frontend/blob/main/packages/widget-attributions/src/Attributions.vue
// These packages are no longer being served correctly, so
// I'm inlining them here.
import gql from "graphql-tag";

export default {
  name: "Attributions",
  props: ["versionUrn"],
  computed: {
    attributionsByRole() {
      if (!this.attributions) {
        return [];
      }
      const data = this.attributions.reduce((arr, a) => {
        // eslint-disable-next-line no-param-reassign
        arr[a.role] = arr[a.role] || [];
        arr[a.role].push(a);
        return arr;
      }, []);
      return Object.entries(data);
    },
  },
  apollo: {
    attributions: {
      query: gql`
        query Attributions($urn: String!) {
          attributions(reference: $urn) {
            edges {
              node {
                id
                role
                name
              }
            }
          }
        }
      `,
      variables() {
        return { urn: this.versionUrn };
      },
      update(data) {
        return data.attributions.edges.map((e) => e.node);
      },
      skip() {
        return this.versionUrn === null;
      },
    },
  },
};
</script>

<style lang="scss" scoped>
.attributions-container {
  flex-direction: column;
  > * {
    font-size: 14px;
  }
  .attribution-row {
    > .label {
      color: var(--sv-widget-attribution-label-text-color, #868e96);
    }
    > .value {
      font-family: var(--sv-widget-attribution-value-font-family, "Noto Serif");
      margin: 0.5em;
    }
    flex-flow: row nowrap;
    margin: 0.75em 0;
  }
}
</style>
