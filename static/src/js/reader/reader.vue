<template>
  <div>
    <template v-if="!ready">
      <div class="wrapper">
        <reader-loader v-show="showLoader" />
      </div>
    </template>
    <div v-else-if="error" class="wrapper" :style="{ margin: 'auto' }">
      <div class="alert alert-danger" role="alert">
        <b>Error</b>: {{ error }}
      </div>
    </div>
    <template v-else>
      <skeleton>
        <template slot="left">
          <widget-passage-ancestors />
          <widget-passage-children />
          <widget-passage-reference />
          <widget-search />
        </template>
        <template slot="body">
          <div class="passage-heading">
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
                <div v-if="leftPassage.error" class="alert text-danger" role="alert">
                  Failed to load <b>{{ leftPassage.urn.toString() }}</b>: {{ leftPassage.error }}
                </div>
                <template v-else>
                  <passage-redirect-notice v-if="leftPassage.redirected" :passage="leftPassage" />
                  <passage-render-text :text="leftPassageText" :highlighting="true" />
                </template>
              </div>
              <div class="right">
                <template v-if="rightText.metadata">
                  <version-selector :versions="versions" :to="toRightPassage" :remove="toRemoveRight">
                    {{ rightText.metadata.label }}
                    <div class="metadata">{{ rightText.metadata.human_lang }} {{ rightText.metadata.kind }}</div>
                  </version-selector>
                  <div v-if="rightPassage.error" class="alert text-danger" role="alert">
                    Failed to load <b>{{ rightPassage.urn.toString() }}</b>: {{ rightPassage.error }}
                  </div>
                  <template v-else>
                    <passage-redirect-notice v-if="rightPassage.redirected" :passage="rightPassage" />
                    <passage-render-text :text="rightPassageText" :highlighting="false" />
                  </template>
                </template>
              </div>
            </template>
            <div v-else>
              <div v-if="leftPassage.error" class="alert text-danger" role="alert">
                Failed to load <b>{{ leftPassage.urn.toString() }}</b>: {{ leftPassage.error }}
              </div>
              <template v-else>
                <passage-redirect-notice v-if="leftPassage.redirected" :passage="leftPassage" />
                <passage-render-text :text="leftPassageText" :highlighting="true" />
              </template>
            </div>
            <div class="pg-right">
              <router-link v-if="passage.metadata.next" :to="toRef(passage.metadata.next.ref)">
                <span>
                  <i :class="['fa', {'fa-chevron-left': text.metadata.rtl, 'fa-chevron-right': !text.metadata.rtl}]"></i>
                </span>
              </router-link>
            </div>
          </div>
        </template>
        <template slot="right">
          <widget-passage-links />
          <widget-text-mode />
          <widget-text-size />
          <widget-highlight />
          <widget-morpheus />
          <widget-token-list />
          <widget-dv-word-list />
        </template>
      </skeleton>
    </template>
  </div>
</template>

<script>
import store from '../store';
import Skeleton from './skeleton';
import PassageHumanReference from './passage-human-reference';
import PassageRenderText from './passage-render-text';
import PassageRedirectNotice from './passage-redirect-notice';
import ReaderLoader from './reader-loader';
import ReaderNavigationMixin from './reader-navigation-mixin';
import VersionSelector from './version-selector';
import WidgetPassageAncestors from './widgets/passage-ancestors';
import WidgetPassageChildren from './widgets/passage-children';
import WidgetPassageReference from './widgets/passage-reference';
import WidgetSearch from './widgets/search';
import WidgetHighlight from './widgets/highlight';
import WidgetPassageLinks from './widgets/passage-links';
import WidgetTextMode from './widgets/text-mode';
import WidgetTextSize from './widgets/text-size';
import WidgetMorpheus from './widgets/morpheus';
import WidgetDvWordList from './widgets/dv-word-list';
import WidgetTokenList from './widgets/dm-token-list';

const widgets = {
  WidgetPassageAncestors,
  WidgetPassageChildren,
  WidgetPassageReference,
  WidgetSearch,
  WidgetPassageLinks,
  WidgetTextMode,
  WidgetTextSize,
  WidgetHighlight,
  WidgetMorpheus,
  WidgetDvWordList,
  WidgetTokenList,
};

export default {
  name: 'Reader',
  store,
  components: {
    Skeleton,
    PassageHumanReference,
    PassageRenderText,
    PassageRedirectNotice,
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
    leftPassageText() {
      return this.$store.state.reader.leftPassageText;
    },
    rightPassageText() {
      return this.$store.state.reader.rightPassageText;
    },
  },
  watch: {
    $route: 'sync',
  },
  mounted() {
    setTimeout(() => { this.showLoader = true; }, 50);
    this.sync({ initial: true }).then(() => {
      this.ready = true;
      window.addEventListener('keyup', this.handleKeyUp);
    });
  },
  beforeDestroy() {
    window.removeEventListener('keyup', this.handleKeyUp);
  },
  methods: {
    sync({ initial = false }) {
      const { leftUrn, rightUrn } = this;
      return this.$store.dispatch('reader/load', { leftUrn, rightUrn, initial });
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
  },
};
</script>
