<template>
  <div class="skeleton-wrapper">

    <div :class="['sidebar', { collapsed: sidebarLeftOpened }]" id="left-sidebar">
      <button class="close-left" v-if="!sidebarLeftOpened" @click="toggleSidebar('left')"><i></i></button>
      <div>
        LEFT PANEL
      </div>
    </div>

    <button class="open-left" v-if="sidebarLeftOpened" @click="toggleSidebar('left')"><i></i></button>

    <section id="content_body">
      CONTENT BODY
    </section>

    <button class="open-right" v-if="sidebarRightOpened" @click="toggleSidebar('right')"><i></i></button>

    <div :class="['sidebar', { collapsed: sidebarRightOpened }]" id="right-sidebar">
      <button class="close-right" v-if="!sidebarRightOpened" @click="toggleSidebar('right')"><i></i></button>
      <div>
        RIGHT PANEL
      </div>
    </div>
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
