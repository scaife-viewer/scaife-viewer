<template>
  <span>
    {{ start.human_reference }}
    <template v-if="end">
      to {{ end.human_reference }}
    </template>
    ({{ start.reference }}<template v-if="end">&ndash; {{ end.reference }}</template>)
  </span>
</template>
<script>
export default {
  name: 'passage-human-reference',
  props: ['metadata'],
  computed: {
    start() {
      return this.metadata.refs.start;
    },
    end() {
      return this.metadata.refs.end;
    }
  }
}
</script>
