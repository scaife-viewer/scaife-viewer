<template functional>
  <span>
    {{ props.metadata.refs.start.human_reference }}
    <template v-if="props.metadata.refs.end">
      to {{ props.metadata.refs.end.human_reference }}
    </template>
    ({{ props.metadata.refs.start.reference }}<template v-if="props.metadata.refs.end">&ndash; {{ props.metadata.refs.end.reference }}</template>)
  </span>
</template>
