<template>
  <div v-if="redirected" class="passage-redirect-alert" role="alert">
    <p>
      Passage reference for
      <b>{{ redirected.previousUrn.value }}</b>
      could not be resolved.
    </p>
    <p>
      Instead, we are showing you
      <b>{{ passage.urn.value }}</b>.
    </p>
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
