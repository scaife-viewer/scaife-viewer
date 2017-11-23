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
        <h1><a v-for="breadcrumb in primaryPassage.text.ancestors" :key="breadcrumb.urn" href="#">{{ breadcrumb.label }}</a></h1>
        <h3><passage-human-reference :passage="primaryPassage"></passage-human-reference></h3>
        <div id="overall" class="overall">
          <div class="text" v-html="primaryPassage.text_html"></div>
        </div>
      </div>
    </section>
    <div :class="['sidebar', { collapsed: sidebarRightOpened }]" id="right-sidebar">
      <div>
        <div class="widget">
          <h2>CTS URN</h2>
          <p>
            <tt><a :href="`https://perseus-cts.eu1.eldarioncloud.com/api/cts?request=GetPassage&amp;urn=${primaryPassage.urn}`">{{ primaryPassage.urn }}</a></tt>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../store';
import PassageHumanReference from './PassageHumanReference';

export default {
  store,
  props: {
    urns: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.$store.dispatch('loadPassages', this.urnList).then(() => {
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
      passages: state => state.reader.passages,
      sidebarLeftOpened: state => state.reader.sidebarLeftOpened,
      sidebarRightOpened: state => state.reader.sidebarRightOpened,
    }),
    urnList() {
      return this.urns.split(' ');
    },
    primaryPassage() {
      return this.passages.get(this.urnList[0]);
    },
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
    PassageHumanReference,
  },
};
</script>
