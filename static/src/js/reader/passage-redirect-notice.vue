<template functional>
  <div v-if="props.passage.redirected" class="alert alert-info text-info text-center" role="alert">
    <b>{{ props.passage.redirected.previousUrn.reference }}</b> did not exist. Instead, we are showing you <b>{{ props.passage.urn.reference }}</b>.
  </div>
</template>
