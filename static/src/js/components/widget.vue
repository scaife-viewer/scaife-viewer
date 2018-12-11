<template>
  <div class="widget">
    <div class="sticky-block">
      <h2>
        <span @click.prevent="toggle">
          <span class="open-toggle">
            <i :class="['fa', open ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
          </span>
          <slot name="header"></slot>
        </span>
        <span v-if="open" class="fixed-toggle" @click.prevent="toggleFix">
          <i :class="['fa', fixed ? 'fa-expand' : 'fa-compress']"></i>
        </span>
      </h2>
      <div v-if="open" class="sticky-body">
        <slot name="sticky"></slot>
      </div>
    </div>
    <div v-if="open" :class="['body', { fixed }]">
      <slot name="body"></slot>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'widget',
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
      toggleFix() {
        this.fixed = !this.fixed;
      },
    },
  };
</script>
