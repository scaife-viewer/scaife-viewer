<template>
  <div class="wrapper" v-if="loaded">
    <div :class="['sidebar', { collapsed: sidebarLeftOpened }]" id="left-sidebar">
      <div>
      </div>
    </div>
    <section id="content_body">
      <button id="left-sidebar-toggle" :class="[{ open: sidebarLeftOpened }]" @click="toggleSidebar('left')"><i></i></button>
      <button id="right-sidebar-toggle" :class="[{ open: sidebarRightOpened }]" @click="toggleSidebar('right')"><i></i></button>
      <div class="passage-heading">
        <a href="/">Library &gt;</a>
        <h1><a v-for="breadcrumb in passage.text.ancestors" :key="breadcrumb.urn" :href="breadcrumb.url">{{ breadcrumb.label }}</a></h1>
        <h3><passage-human-reference :passage="passage"></passage-human-reference></h3>
        <div id="overall" class="overall" :dir="passage.rtl ? 'rtl' : 'ltr'">
          <div class="pg-left">
            <a v-if="passage.prev" href="#" @click.prevent="setPassage(passage.prev.urn)"><span><i :class="['fa', {'fa-chevron-left': !passage.rtl, 'fa-chevron-right': passage.rtl}]"></i></span></a>
          </div>
          <div class="text" v-html="passage.text_html"></div>
          <div class="pg-right">
            <a v-if="passage.next" href="#" @click.prevent="setPassage(passage.next.urn)"><span><i :class="['fa', {'fa-chevron-left': passage.rtl, 'fa-chevron-right': !passage.rtl}]"></i></span></a>
          </div>
        </div>
      </div>
    </section>
    <div :class="['sidebar', { collapsed: sidebarRightOpened }]" id="right-sidebar">
      <div>
        <passage-links-widget></passage-links-widget>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../../store';
import PassageHumanReference from './PassageHumanReference';
import PassageLinksWidget from './widgets/PassageLinksWidget';

export default {
  store,
  props: {
    urn: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.setPassage(this.urn).then(() => {
      this.loaded = true;
    });
  },
  data() {
    return {
      loaded: false,
    };
  },
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
    setPassage(urn) {
      window.history.pushState({}, urn, `/reader/${urn}/`);
      return this.$store.dispatch('setPassage', urn);
    },
  },
  components: {
    PassageHumanReference,
    PassageLinksWidget,
  },
};
</script>
