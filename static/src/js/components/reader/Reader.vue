<template>
  <div class="wrapper" v-if="loaded">
    <div :class="['sidebar', { collapsed: sidebarLeftOpened }]" id="left-sidebar">
      <div>
        <passage-ancestor-widget></passage-ancestor-widget>
        <passage-children-widget></passage-children-widget>
        <passage-reference-widget></passage-reference-widget>
      </div>
    </div>
    <section id="content_body">
      <button id="left-sidebar-toggle" :class="[{ open: !sidebarLeftOpened }]" @click="toggleSidebar('left')"><i></i></button>
      <button id="right-sidebar-toggle" :class="[{ open: !sidebarRightOpened }]" @click="toggleSidebar('right')"><i></i></button>
      <div class="passage-heading">
        <a href="/">Library &gt;</a>
        <h1><a v-for="breadcrumb in passage.text.ancestors" :key="breadcrumb.urn" :href="breadcrumb.url">{{ breadcrumb.label }}</a></h1>
        <h3><passage-human-reference :passage="passage"></passage-human-reference></h3>
      </div>
      <version-selector v-if="!rightPassage && versions.length > 1" :versions="versions" :to="toRightPassage">
        <i class="fa fa-columns"></i>
        add parallel version
      </version-selector>
      <div id="overall" class="overall" :dir="passage.rtl ? 'rtl' : 'ltr'">
        <div class="pg-left">
          <router-link v-if="passage.prev" :to="toRef(passage.prev.ref)"><span><i :class="['fa', {'fa-chevron-left': !passage.rtl, 'fa-chevron-right': passage.rtl}]"></i></span></router-link>
        </div>
        <template v-if="rightPassage">
          <div class="left">
            <version-selector :versions="versions" :to="toPassage" :remove="toRemoveLeft">
              {{ passage.text.label }}
              <div class="metadata">{{ passage.text.human_lang }} {{ passage.text.kind }}</div>
            </version-selector>
            <passage-render-text :passage="passage" :loading="passageLoading"></passage-render-text>
          </div>
          <div class="right">
            <version-selector :versions="versions" :to="toRightPassage" :remove="toRemoveRight">
              {{ rightPassage.text.label }}
              <div class="metadata">{{ rightPassage.text.human_lang }} {{ rightPassage.text.kind }}</div>
            </version-selector>
            <passage-render-text :passage="rightPassage" :loading="rightPassageLoading"></passage-render-text>
          </div>
        </template>
        <passage-render-text v-else :passage="passage" :loading="passageLoading"></passage-render-text>
        <div class="pg-right">
          <router-link v-if="passage.next" :to="toRef(passage.next.ref)"><span><i :class="['fa', {'fa-chevron-left': passage.rtl, 'fa-chevron-right': !passage.rtl}]"></i></span></router-link>
        </div>
      </div>
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
import parseURN from '../../urn';
import PassageRenderText from './PassageRenderText';
import PassageHumanReference from './PassageHumanReference';
import VersionSelector from './VersionSelector';
import PassageAncestorWidget from './widgets/PassageAncestorWidget';
import PassageChildrenWidget from './widgets/PassageChildrenWidget';
import PassageReferenceWidget from './widgets/PassageReferenceWidget';
import PassageLinksWidget from './widgets/PassageLinksWidget';
import TextSizeWidget from './widgets/TextSizeWidget';

export default {
  store,
  props: {
    urn: {
      type: String,
      required: true,
    },
    rightUrn: {
      type: String,
      required: false,
    },
  },
  mounted() {
    window.addEventListener('keyup', this.handleKeyUp);
    this.loadData();
  },
  beforeDestroy() {
    window.removeEventListener('keyup', this.handleKeyUp);
  },
  data() {
    return {
      loaded: false,
    };
  },
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
      rightPassage: state => state.reader.rightPassage,
      passageLoading: state => state.reader.passageLoading,
      rightPassageLoading: state => state.reader.rightPassageLoading,
      versions: state => state.reader.versions,
      sidebarLeftOpened: state => state.reader.sidebarLeftOpened,
      sidebarRightOpened: state => state.reader.sidebarRightOpened,
    }),
  },
  watch: {
    $route: 'loadData',
  },
  methods: {
    loadData() {
      const pending = [];
      if (!this.passage || this.urn !== this.passage.urn) {
        pending.push(this.$store.dispatch('setPassage', this.urn));
      }
      if (this.rightUrn && (!this.rightPassage || this.rightUrn !== this.rightPassage.urn)) {
        pending.push(this.$store.dispatch('setRightPassage', this.rightUrn));
      }
      Promise.all(pending).then(() => {
        this.loaded = true;
      });
    },
    handleKeyUp(e) {
      if (e.key === 'ArrowLeft') {
        if (this.passage.prev) {
          this.$router.push(this.toRef(this.passage.prev.ref));
        }
      } else if (e.key === 'ArrowRight') {
        if (this.passage.next) {
          this.$router.push(this.toRef(this.passage.next.ref));
        }
      }
    },
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
    toPassage(urn) {
      const p = parseURN(urn);
      if (!p.reference && this.passage) {
        const { reference: existingReference } = parseURN(this.passage.urn);
        urn += `:${existingReference}`;
      }
      return { name: 'reader', params: { urn }, query: this.$route.query };
    },
    toRightPassage(urn) {
      const p = parseURN(urn);
      return { name: 'reader', params: this.$route.params, query: { right: p.version } };
    },
    toRef(reference) {
      const p = parseURN(this.urn);
      const urn = `urn:${p.urnNamespace}:${p.ctsNamespace}:${p.textGroup}.${p.work}.${p.version}:${reference}`;
      return { name: 'reader', params: { urn }, query: this.$route.query };
    },
    toRemoveLeft() {
      return { name: 'reader', params: { urn: this.rightPassage.urn } };
    },
    toRemoveRight() {
      return { name: 'reader', params: { urn: this.passage.urn } };
    },
  },
  components: {
    PassageRenderText,
    PassageHumanReference,
    VersionSelector,
    PassageAncestorWidget,
    PassageChildrenWidget,
    PassageReferenceWidget,
    PassageLinksWidget,
    TextSizeWidget,
  },
};
</script>
