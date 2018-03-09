<template functional>
  <div v-if="props.passage.redirected" class="passage-redirect-alert" role="alert">
    Passage reference
    <b>{{ props.passage.redirected.previousUrn.reference }}</b>
    could not be resolved.
    Instead, we are showing you
    <b>{{ props.passage.urn.reference }}</b>.
  </div>
</template>
