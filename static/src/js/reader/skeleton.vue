<template>
  <div class="wrapper">

    <div :class="['sidebar', { collapsed: !sidebarLeftOpened, 'both-opened': sidebarLeftOpened && sidebarRightOpened }]" id="left-sidebar">
      <button class="close-left" v-if="sidebarLeftOpened" @click="toggleSidebar('left')"><icon name="arrow-left"></icon></button>
      <div>
        <slot name="left"></slot>
      </div>
    </div>

    <button class="open-left" v-if="!sidebarLeftOpened" @click="toggleSidebar('left')"><icon name="arrow-right"></icon></button>

    <section id="content_body">
      <slot name="body"></slot>
    </section>

    <button class="open-right" v-if="!sidebarRightOpened" @click="toggleSidebar('right')"><icon name="arrow-left"></icon></button>

    <div :class="['sidebar', { collapsed: !sidebarRightOpened, 'both-opened': sidebarLeftOpened && sidebarRightOpened }]" id="right-sidebar">
      <button class="close-right" v-if="sidebarRightOpened" @click="toggleSidebar('right')"><icon name="arrow-right"></icon></button>
      <div>
        <slot name="right"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Skeleton',
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
          this.$store.commit(constants.READER_TOGGLE_SIDEBAR_LEFT);
          break;
        case 'right':
          this.$store.commit(constants.READER_TOGGLE_SIDEBAR_RIGHT);
          break;
        default:
      }
    },
  },
};
</script>
