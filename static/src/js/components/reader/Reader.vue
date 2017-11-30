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
      <button id="left-sidebar-toggle" :class="[{ open: sidebarLeftOpened }]" @click="toggleSidebar('left')"><i></i></button>
      <button id="right-sidebar-toggle" :class="[{ open: sidebarRightOpened }]" @click="toggleSidebar('right')"><i></i></button>
      <div class="passage-heading">
        <a href="/">Library &gt;</a>
        <h1><a v-for="breadcrumb in passage.text.ancestors" :key="breadcrumb.urn" :href="breadcrumb.url">{{ breadcrumb.label }}</a></h1>
        <h3><passage-human-reference :passage="passage"></passage-human-reference></h3>
      </div>
      <version-selector v-if="!rightPassage && versions.length > 1" :versions="versions" :handler="setRightPassageAndHistory">
        <i class="fa fa-columns"></i>
        add parallel version
      </version-selector>
      <div id="overall" class="overall" :dir="passage.rtl ? 'rtl' : 'ltr'">
        <div class="pg-left">
          <a v-if="passage.prev" href="#" @click.prevent="setRefAndHistory(passage.prev.ref)"><span><i :class="['fa', {'fa-chevron-left': !passage.rtl, 'fa-chevron-right': passage.rtl}]"></i></span></a>
        </div>
        <template v-if="rightPassage">
          <div class="left">
            <version-selector :versions="versions" :handler="setPassageAndHistory" :removal="removeLeft">
              {{ passage.text.label }}
              <div class="metadata">{{ passage.text.human_lang }} {{ passage.text.kind }}</div>
            </version-selector>
            <passage-render-text :passage="passage"></passage-render-text>
          </div>
          <div class="right">
            <version-selector :versions="versions" :handler="setRightPassageAndHistory" :removal="removeRight">
              {{ rightPassage.text.label }}
              <div class="metadata">{{ rightPassage.text.human_lang }} {{ rightPassage.text.kind }}</div>
            </version-selector>
            <passage-render-text :passage="rightPassage"></passage-render-text>
          </div>
        </template>
        <passage-render-text v-else :passage="passage"></passage-render-text>
        <div class="pg-right">
          <a v-if="passage.next" href="#" @click.prevent="setRefAndHistory(passage.next.ref)"><span><i :class="['fa', {'fa-chevron-left': passage.rtl, 'fa-chevron-right': !passage.rtl}]"></i></span></a>
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
import { mapState, mapActions } from 'vuex';
import store from '../../store';
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
    const pending = [];
    pending.push(this.setPassage(this.urn));
    if (this.rightUrn) {
      pending.push(this.setRightPassage(this.rightUrn));
    }
    Promise.all(pending).then(() => {
      this.loaded = true;
      this.setHistory();
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
      rightPassage: state => state.reader.rightPassage,
      versions: state => state.reader.versions,
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
    removeLeft() {
      const rightUrn = this.rightPassage.urn;
      this.$store.dispatch('setRightPassage', null).then(() => {
        this.$store.dispatch('setPassage', rightUrn).then(() => {
          this.setHistory();
        });
      });
    },
    removeRight() {
      this.$store.dispatch('setRightPassage', null).then(() => {
        this.setHistory();
      });
    },
    ...mapActions([
      'setPassage',
      'setRightPassage',
      'setRef',
      'setPassageAndHistory',
      'setRightPassageAndHistory',
      'setRefAndHistory',
      'setHistory',
    ]),
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
