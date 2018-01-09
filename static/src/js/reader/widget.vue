<template>
  <div class="widget">
    <h2 @click.prevent="toggle">
      <span class="summary" v-if="!open"><slot name="summary"></slot></span>
      <slot name="header"></slot>
    </h2>
    <p v-if="open">
      <slot name="body"></slot>
    </p>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        open: true,
      };
    },
    methods: {
      toggle() {
        this.open = !this.open;
      },
    },
  };
</script>
