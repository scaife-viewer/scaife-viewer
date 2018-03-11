<template>
  <div class="wrapper">
    <template>
      <button class="left-toggle" v-if="sidebarLeftOpened" @click="toggleSidebar('left')"><i></i></button>
      <button class="right-toggle" v-if="sidebarRightOpened" @click="toggleSidebar('right')"><i></i></button>
      <div :class="['sidebar', { collapsed: sidebarLeftOpened }]" id="left-sidebar">
        <button class="right-toggle" v-if="!sidebarLeftOpened" @click="toggleSidebar('left')"><i></i></button>
        <div>
          LEFT PANEL
        </div>
      </div>
      <section id="content_body">
        CONTENT BODY
      </section>
      <div :class="['sidebar', { collapsed: sidebarRightOpened }]" id="right-sidebar">
        <button class="left-toggle" v-if="!sidebarRightOpened" @click="toggleSidebar('right')"><i></i></button>
        <div>
          RIGHT PANEL
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import store from '../store';

export default {
  name: 'Skeleton',
  store,
  computed: {
    sidebarLeftOpened() {
      return this.$store.state.reader.sidebarLeftOpened;
    },
    sidebarRightOpened() {
      return this.$store.state.reader.sidebarRightOpened;
    },
  },
  methods: {
    toggleSidebar(side) {
      switch (side) {
        case 'left':
          this.$store.commit('reader/toggleSidebarLeft');
          break;
        case 'right':
          this.$store.commit('reader/toggleSidebarRight');
          break;
        default:
      }
    },
  },
};
</script>
