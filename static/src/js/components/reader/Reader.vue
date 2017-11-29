<template>
  <div class="wrapper">
    <div :class="['sidebar', { collapsed: sidebarLeftOpened }]" id="left-sidebar">
      <div>
        <passage-ancestor-widget></passage-ancestor-widget>
        <passage-children-widget></passage-children-widget>
        <passage-reference-widget></passage-reference-widget>
      </div>
    </div>
    <section id="content_body">
      <button id="left-sidebar-toggle" :class="[{ open: sidebarLeftOpened }]" @click="toggleSidebar('left')"><i></i></button>
      <button id="right-sidebar-toggle" :class="[{ open: sidebarRightOpened }]" @click="toggleSidebar('right')"><i></i></button>
      <slot></slot>
    </section>
    <div :class="['sidebar', { collapsed: sidebarRightOpened }]" id="right-sidebar">
      <div>
        <passage-links-widget></passage-links-widget>
        <text-size-widget></text-size-widget>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../../store';
import PassageAncestorWidget from './widgets/PassageAncestorWidget';
import PassageChildrenWidget from './widgets/PassageChildrenWidget';
import PassageReferenceWidget from './widgets/PassageReferenceWidget';
import PassageLinksWidget from './widgets/PassageLinksWidget';
import TextSizeWidget from './widgets/TextSizeWidget';

export default {
  store,
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
      sidebarLeftOpened: state => state.reader.sidebarLeftOpened,
      sidebarRightOpened: state => state.reader.sidebarRightOpened,
    }),
  },
  methods: {
    toggleSidebar(side) {
      switch (side) {
        case 'left':
          this.$store.commit('toggleSidebarLeft');
          break;
        case 'right':
          this.$store.commit('toggleSidebarRight');
          break;
        default:
      }
    },
  },
  components: {
    PassageAncestorWidget,
    PassageChildrenWidget,
    PassageReferenceWidget,
    PassageLinksWidget,
    TextSizeWidget,
  },
};
</script>
