<template>
  <div v-if="redirected" class="passage-redirect-alert" role="alert">
    Passage reference
    <b>{{ redirected.previousUrn.reference }}</b>
    could not be resolved.
    Instead, we are showing you
    <b>{{ passage.urn.reference }}</b>.
  </div>
</template>
<script>
export default {
  name: 'passage-redirect-notice',
  props: ['passage'],
  computed: {
    redirected() {
      return this.passage.redirected;
    }
  }
}
</script>
