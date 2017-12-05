<template>
  <div class="btn-group btn-group-left">
    <button type="button" class="btn btn-light dropdown-toggle dropdown-toggle-split" @click="toggleMenu" aria-haspopup="true" aria-expanded="false">
      <span class="sr-only">Toggle Dropdown</span>
    </button>
    <div class="version-select">
      <slot></slot>
    </div>
    <div :class="['version-option', 'dropdown-menu', { show }]">
      <router-link v-for="version in versions" :key="version.urn" class="dropdown-item" :to="to(version.urn)" @click.native="handleItemClick">
        {{ version.label }}
        <div class="metadata">{{ version.human_lang }} {{ version.kind }}</div>
      </router-link>
      <template v-if="remove">
        <div class="dropdown-divider"></div>
        <router-link class="dropdown-item remove" :to="remove" @click.native="handleRemoveClick">remove</router-link>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: ['versions', 'to', 'remove'],
  data() {
    return {
      show: false,
    };
  },
  methods: {
    toggleMenu() {
      this.show = !this.show;
    },
    handleItemClick() {
      this.show = false;
    },
    handleRemoveClick() {
      this.show = false;
    },
  },
};
</script>
