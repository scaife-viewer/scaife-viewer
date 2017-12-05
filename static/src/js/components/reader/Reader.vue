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
      <version-selector v-if="!rightUrn && versions.length > 1" :versions="versions" :to="toRightPassage">
        <i class="fa fa-columns"></i>
        add parallel version
      </version-selector>
      <div id="overall" class="overall" :dir="passage.rtl ? 'rtl' : 'ltr'">
        <div class="pg-left">
          <router-link v-if="passage.prev" :to="toRef(passage.prev.ref)"><span><i :class="['fa', {'fa-chevron-left': !passage.rtl, 'fa-chevron-right': passage.rtl}]"></i></span></router-link>
        </div>
        <template v-if="rightUrn">
          <div class="left">
            <div v-if="passageError" class="alert alert-danger" role="alert">
              Failed to load <b>{{ urn }}</b>: {{ passageError }}
            </div>
            <template v-else>
              <version-selector :versions="versions" :to="toPassage" :remove="toRemoveLeft">
                {{ passage.text.label }}
                <div class="metadata">{{ passage.text.human_lang }} {{ passage.text.kind }}</div>
              </version-selector>
              <passage-render-text :passage="passage" :loading="passageLoading"></passage-render-text>
            </template>
          </div>
          <div class="right">
            <div v-if="rightPassageError" class="alert alert-danger" role="alert">
              Failed to load <b>{{ rightUrn }}</b>: {{ rightPassageError }}
            </div>
            <template v-else>
              <version-selector :versions="versions" :to="toRightPassage" :remove="toRemoveRight">
                {{ rightPassage.text.label }}
                <div class="metadata">{{ rightPassage.text.human_lang }} {{ rightPassage.text.kind }}</div>
              </version-selector>
              <passage-render-text :passage="rightPassage" :loading="rightPassageLoading"></passage-render-text>
            </template>
          </div>
        </template>
        <template v-else>
          <div v-if="passageError" class="alert alert-danger" role="alert">
            Failed to load <b>{{ urn }}</b>: {{ passageError }}
          </div>
          <template v-else>
            <passage-render-text :passage="passage" :loading="passageLoading"></passage-render-text>
          </template>
        </template>
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
import PassageRenderText from './PassageRenderText';
import PassageHumanReference from './PassageHumanReference';
import VersionSelector from './VersionSelector';
import PassageAncestorWidget from './widgets/PassageAncestorWidget';
import PassageChildrenWidget from './widgets/PassageChildrenWidget';
import PassageReferenceWidget from './widgets/PassageReferenceWidget';
import PassageLinksWidget from './widgets/PassageLinksWidget';
import TextSizeWidget from './widgets/TextSizeWidget';
import { toPassage, toRightPassage, toRef, toRemoveLeft, toRemoveRight } from './utils';

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
      passageError: state => state.reader.passageError,
      rightPassageError: state => state.reader.rightPassageError,
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
      } else {
        pending.push(this.$store.dispatch('setRightPassage', null));
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
    toPassage,
    toRightPassage,
    toRef,
    toRemoveLeft,
    toRemoveRight,
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
