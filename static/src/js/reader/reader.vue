<template>
  <div class="wrapper">
    <template v-if="!ready">
      <reader-loader v-show="showLoader" />
    </template>
    <div v-else-if="error" :style="{ margin: 'auto' }">
      <div class="alert alert-danger" role="alert">
        <b>Error</b>: {{ error }}
      </div>
    </div>
    <template v-else>
      <div :class="['sidebar', { collapsed: sidebarLeftOpened }]" id="left-sidebar">
        <div>
          <widget-passage-ancestors />
          <widget-passage-children />
          <widget-passage-reference />
        </div>
      </div>
      <section id="content_body">
        <button id="left-sidebar-toggle" :class="[{ open: !sidebarLeftOpened }]" @click="toggleSidebar('left')"><i></i></button>
        <button id="right-sidebar-toggle" :class="[{ open: !sidebarRightOpened }]" @click="toggleSidebar('right')"><i></i></button>
        <div class="passage-heading">
          <a href="/">Library &gt;</a>
          <h1>
            <template v-for="(breadcrumb, idx) in text.metadata.ancestors">
              <a :key="breadcrumb.urn" :href="breadcrumb.url">{{ breadcrumb.label }}</a><template v-if="idx != text.metadata.ancestors.length - 1">, </template>
            </template>
          </h1>
          <template v-if="!rightPassage">
            <h2>{{ leftText.metadata.label }}</h2>
            <h3><passage-human-reference :metadata="leftPassage.metadata" /></h3>
          </template>
        </div>
        <version-selector v-if="!rightPassage && versions.length > 1" :versions="versions" :to="toRightPassage">
          <i class="fa fa-columns"></i>
          add parallel version
        </version-selector>
        <div id="overall" class="overall" :dir="text.metadata.rtl ? 'rtl' : 'ltr'">
          <div class="pg-left">
            <router-link v-if="passage.metadata.prev" :to="toRef(passage.metadata.prev.ref)">
              <span>
                <i :class="['fa', {'fa-chevron-left': !text.metadata.rtl, 'fa-chevron-right': text.metadata.rtl}]"></i>
              </span>
            </router-link>
          </div>
          <template v-if="rightUrn">
            <div class="left">
              <version-selector :versions="versions" :to="toPassage" :remove="toRemoveLeft">
                {{ leftText.metadata.label }}
                <div class="metadata">{{ leftText.metadata.human_lang }} {{ leftText.metadata.kind }}</div>
              </version-selector>
              <div v-if="leftPassage.error" class="alert alert-danger" role="alert">
                Failed to load <b>{{ leftPassage.urn.toString() }}</b>: {{ leftPassage.error }}
              </div>
              <passage-render-text v-else :passage="leftPassage" />
            </div>
            <div class="right">
              <version-selector :versions="versions" :to="toRightPassage" :remove="toRemoveRight">
                {{ rightText.metadata.label }}
                <div class="metadata">{{ rightText.metadata.human_lang }} {{ rightText.metadata.kind }}</div>
              </version-selector>
              <div v-if="rightPassage.error" class="alert alert-danger" role="alert">
                Failed to load <b>{{ rightPassage.urn.toString() }}</b>: {{ rightPassage.error }}
              </div>
              <passage-render-text v-else :passage="rightPassage" />
            </div>
          </template>
          <template v-else>
            <div v-if="leftPassage.error" class="alert alert-danger" role="alert">
              Failed to load <b>{{ leftPassage.urn.toString() }}</b>: {{ leftPassage.error }}
            </div>
            <passage-render-text v-else :passage="leftPassage" />
          </template>
          <div class="pg-right">
            <router-link v-if="passage.metadata.next" :to="toRef(passage.metadata.next.ref)">
              <span>
                <i :class="['fa', {'fa-chevron-left': text.metadata.rtl, 'fa-chevron-right': !text.metadata.rtl}]"></i>
              </span>
            </router-link>
          </div>
        </div>
      </section>
      <div :class="['sidebar', { collapsed: sidebarRightOpened }]" id="right-sidebar">
        <div>
          <widget-passage-links />
          <widget-text-size />
          <widget-selected-word />
          <widget-token-list />
          <widget-dv-word-list />
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import store from '../store';
import PassageHumanReference from './passage-human-reference';
import PassageRenderText from './passage-render-text';
import ReaderLoader from './reader-loader';
import ReaderNavigationMixin from './reader-navigation-mixin';
import VersionSelector from './version-selector';
import WidgetPassageAncestors from './widgets/passage-ancestors';
import WidgetPassageChildren from './widgets/passage-children';
import WidgetPassageReference from './widgets/passage-reference';
import WidgetPassageLinks from './widgets/passage-links';
import WidgetTextSize from './widgets/text-size';
import WidgetDvWordList from './widgets/dv-word-list';
import WidgetTokenList from './widgets/dm-token-list';
import WidgetSelectedWord from './widgets/selected-word';

const widgets = {
  WidgetPassageAncestors,
  WidgetPassageChildren,
  WidgetPassageReference,
  WidgetPassageLinks,
  WidgetTextSize,
  WidgetSelectedWord,
  WidgetDvWordList,
  WidgetTokenList,
};

export default {
  name: 'Reader',
  store,
  components: {
    PassageHumanReference,
    PassageRenderText,
    ReaderLoader,
    VersionSelector,
    ...widgets,
  },
  mixins: [
    ReaderNavigationMixin,
  ],
  props: {
    leftUrn: {
      required: true,
    },
    rightUrn: {
      required: false,
    },
  },
  data() {
    return {
      ready: false,
      showLoader: false,
    };
  },
  computed: {
    error() {
      return this.$store.state.reader.error;
    },
    sidebarLeftOpened() {
      return this.$store.state.reader.sidebarLeftOpened;
    },
    sidebarRightOpened() {
      return this.$store.state.reader.sidebarRightOpened;
    },
    versions() {
      return this.$store.state.reader.versions;
    },
    text() {
      return this.$store.getters['reader/text'];
    },
    leftText() {
      return this.$store.state.reader.leftText;
    },
    rightText() {
      return this.$store.state.reader.rightText;
    },
    passage() {
      return this.$store.getters['reader/passage'];
    },
    leftPassage() {
      return this.$store.state.reader.leftPassage;
    },
    rightPassage() {
      return this.$store.state.reader.rightPassage;
    },
  },
  watch: {
    $route: 'sync',
  },
  mounted() {
    setTimeout(() => { this.showLoader = true; }, 50);
    this.sync().then(() => {
      this.ready = true;
      window.addEventListener('keyup', this.handleKeyUp);
      this.selectWord();
    });
  },
  beforeDestroy() {
    window.removeEventListener('keyup', this.handleKeyUp);
  },
  methods: {
    sync() {
      return this.$store.dispatch('reader/load', {
        leftUrn: this.leftUrn,
        rightUrn: this.rightUrn,
      });
    },
    handleKeyUp(e) {
      if (e.key === 'ArrowLeft') {
        let ref;
        if (this.text.metadata.rtl) {
          if (this.passage.metadata.next) {
            ref = this.passage.metadata.next.ref; // eslint-disable-line prefer-destructuring
          }
        }
        if (!this.text.metadata.rtl) {
          if (this.passage.metadata.prev) {
            ref = this.passage.metadata.prev.ref; // eslint-disable-line prefer-destructuring
          }
        }
        if (ref) {
          this.$router.push(this.toRef(ref));
        }
      } else if (e.key === 'ArrowRight') {
        let ref;
        if (this.text.metadata.rtl) {
          if (this.passage.metadata.prev) {
            ref = this.passage.metadata.prev.ref; // eslint-disable-line prefer-destructuring
          }
        }
        if (!this.text.metadata.rtl) {
          if (this.passage.metadata.next) {
            ref = this.passage.metadata.next.ref; // eslint-disable-line prefer-destructuring
          }
        }
        if (ref) {
          this.$router.push(this.toRef(ref));
        }
      }
    },
    selectWord() {
      const [, w, i] = /^@([^[]+)(?:\[(\d+)\])?$/.exec(this.$route.query.highlight);
      this.$store.dispatch('reader/selectWord', { word: { w, i } });
    },
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
