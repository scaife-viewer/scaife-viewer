<template>
  <div class="wrapper">

    <div :class="['sidebar', { collapsed: !sidebarLeftOpened, 'both-opened': sidebarLeftOpened && sidebarRightOpened }]" id="left-sidebar">
      <button class="close-left" v-if="sidebarLeftOpened" @click="toggleSidebar('left')"><i></i></button>
      <div>
        <slot name="left"></slot>
      </div>
    </div>

    <button class="open-left" v-if="!sidebarLeftOpened" @click="toggleSidebar('left')"><i></i></button>

    <section id="content_body">
      <slot name="body"></slot>
    </section>

    <button class="open-right" v-if="!sidebarRightOpened" @click="toggleSidebar('right')"><i></i></button>

    <div :class="['sidebar', { collapsed: !sidebarRightOpened, 'both-opened': sidebarLeftOpened && sidebarRightOpened }]" id="right-sidebar">
      <button class="close-right" v-if="sidebarRightOpened" @click="toggleSidebar('right')"><i></i></button>
      <div>
        <slot name="right"></slot>
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
