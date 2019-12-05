<template>
  <div class="widget">
    <div class="sticky-block">
      <h2>
        <span @click.prevent="toggle">
          <span class="open-toggle">
            <icon name="chevron-down" v-if="open"></icon>
            <icon name="chevron-right" v-else></icon>
          </span>
          <slot name="header"></slot>
        </span>
        <span v-if="open" class="fixed-toggle" @click.prevent="toggleFix">
          <icon name="expand-arrows-alt" v-if="fixed"></icon>
          <icon name="compress-arrows-alt" v-else></icon>
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
    name: 'base-widget',
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
