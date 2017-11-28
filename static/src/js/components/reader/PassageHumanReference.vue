<template functional>
  <span>
    {{ props.passage.refs.start.human_reference }}
    <template v-if="props.passage.refs.end">
      to {{ props.passage.refs.end.human_reference }}
    </template>
    ({{ props.passage.refs.start.reference }}<template v-if="props.passage.refs.end">&ndash; {{ props.passage.refs.end.reference }}</template>)
  </span>
</template>
