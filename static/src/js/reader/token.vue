<template>
  <span :class="[t]"><slot></slot></span>
</template>

<script>
export default {
  name: 'Token',
  props: {
    t: {
      type: String,
      required: true,
    },
  },
};
</script>
