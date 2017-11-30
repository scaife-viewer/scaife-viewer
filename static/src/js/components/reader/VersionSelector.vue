<template>
  <div class="btn-group btn-group-left">
    <button type="button" class="btn btn-light dropdown-toggle dropdown-toggle-split" @click="toggleMenu" aria-haspopup="true" aria-expanded="false">
      <span class="sr-only">Toggle Dropdown</span>
    </button>
    <div class="version-select">
      <slot></slot>
    </div>
    <div :class="['version-option', 'dropdown-menu', { show }]">
      <a v-for="version in versions" :key="version.urn" class="dropdown-item" href="#" @click.prevent="handleItemClick(version.urn)">
        {{ version.label }}
        <div class="metadata">{{ version.human_lang }} {{ version.kind }}</div>
      </a>
      <template v-if="removal">
        <div class="dropdown-divider"></div>
        <a class="dropdown-item remove" href="#" @click.prevent="handleRemoveClick">remove</a>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: ['versions', 'handler', 'removal'],
  data() {
    return {
      show: false,
    };
  },
  methods: {
    toggleMenu() {
      this.show = !this.show;
    },
    handleItemClick(urn) {
      this.show = false;
      this.handler(urn);
    },
    handleRemoveClick() {
      this.show = false;
      this.removal();
    },
  },
};
</script>
