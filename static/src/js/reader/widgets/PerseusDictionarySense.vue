<template>
  <div>
    <article>
      <p>
        <strong v-if="Boolean(label)" v-text="label"></strong>
        <span v-if="Boolean(definition)" v-html="definition"></span>
      </p>
      <p v-if="(citations || []).length > 0">
        <span
          v-for="citation in citations"
          :key="citation.urn"
        >{{ citation.data.ref }} </span>
      </p>
    </article>

    <div v-for="(child, index) in children" :key="index">
      <perseus-dictionary-sense
        :children="child.children"
        :citations="child.citations"
        :definition="child.definition"
        :label="`${label ? label + '.' : ''}${child.label ? child.label : ''}`"
        :urn="child.urn" />
    </div>
  </div>
</template>

<script>
  export default {
    name: "perseus-dictionary-sense",
    props: {
      children: {
        type: Array,
        default: () => []
      },
      citations: {
        type: Array,
        default: () => [],
      },
      definition: String,
      label: String,
      urn: {
        type: String,
        required: true,
      }
    }
  }
</script>

<style>
lem {
  font-weight: bold;
}

.mb-2 {
  margin-bottom: 2rem;
}
</style>
