<template>
  <div class="widget">
    <h2>
      <span @click.prevent="toggle">
        <span class="open-toggle">
          <i :class="['fa', {'fa-chevron-right': !open, 'fa-chevron-down': open}]"></i>
        </span>
        <slot name="header"></slot>
      </span>
      <span v-if="open" class="fixed-toggle" @click.prevent="toggle_fix">
        <i :class="['fa', {'fa-compress': !fixed, 'fa-expand': fixed}]"></i>
      </span>
    </h2>
    <p v-if="open" :class="{ fixed }">
      <slot name="body"></slot>
    </p>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        open: true,
        fixed: true,
      };
    },
    methods: {
      toggle() {
        this.open = !this.open;
      },
      toggle_fix() {
        this.fixed = !this.fixed;
      },
    },
  };
</script>
