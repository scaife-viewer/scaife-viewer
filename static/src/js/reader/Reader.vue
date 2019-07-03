<template>
  <div>
    <template v-if="!ready">
      <div class="wrapper">
        <page-loader v-show="showLoader" />
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
          <version-selector v-if="canSelectVersions" :versions="versions" :to="toRightPassage">
            <icon name="columns"></icon>
            add parallel version
          </version-selector>
          <div id="overall" class="overall" :dir="text.metadata.rtl ? 'rtl' : 'ltr'">
            <div :class="lowerPassageText ? 'upper' : 'upper-lower'">
              <div class="pg-left">
                <router-link v-if="passage.metadata.prev" :to="toRef(passage.metadata.prev.ref)">
                  <span>
                    <icon name="chevron-right" v-if="text.metadata.rtl"></icon>
                    <icon name="chevron-left" v-else></icon>
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
                  <template v-if="rightText && rightText.metadata">
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
                    <icon name="chevron-left" v-if="text.metadata.rtl"></icon>
                    <icon name="chevron-right" v-else></icon>
                  </span>
                </router-link>
              </div>
            </div>
            <div class="lower" v-if="lowerPassageText">
              <passage-render-text :text="lowerPassageText" :highlighting="false" />
            </div>
          </div>
        </template>
        <template slot="right">
          <widget-passage-links />
          <widget-text-mode />
          <widget-text-size />
          <widget-text-width />
          <widget-highlight />
          <widget-passage-exports />
          <widget-morpheus />
          <widget-token-list />
          <widget-word-list />
          <widget-new-alexandria-commentary />
        </template>
      </skeleton>
    </template>
  </div>
</template>

<script>
import constants from '../constants';
import Skeleton from './Skeleton.vue';
import PassageHumanReference from './PassageHumanReference.vue';
import PassageRenderText from './PassageRenderText.vue';
import PassageRedirectNotice from './PassageRedirectNotice.vue';
import ReaderNavigationMixin from '../mixins/ReaderNavigationMixin.vue';
import URN from '../urn';
import VersionSelector from './VersionSelector.vue';
import WidgetPassageAncestors from './widgets/WidgetPassageAncestors.vue';
import WidgetPassageChildren from './widgets/WidgetPassageChildren.vue';
import WidgetPassageReference from './widgets/WidgetPassageReference.vue';
import WidgetSearch from './widgets/WidgetSearch.vue';
import WidgetHighlight from './widgets/WidgetHighlight.vue';
import WidgetPassageLinks from './widgets/WidgetPassageLinks.vue';
import WidgetPassageExports from './widgets/WidgetPassageExports.vue';
import WidgetTextMode from './widgets/WidgetTextMode.vue';
import WidgetTextSize from './widgets/WidgetTextSize.vue';
import WidgetMorpheus from './widgets/WidgetMorpheus.vue';
import WidgetWordList from './widgets/WidgetWordList.vue';
import WidgetTokenList from './widgets/WidgetTokenList.vue';
import WidgetNewAlexandriaCommentary from './widgets/WidgetNewAlexandriaCommentary.vue';
import WidgetTextWidth from './widgets/WidgetTextWidth.vue';

const widgets = {
  WidgetPassageAncestors,
  WidgetPassageChildren,
  WidgetPassageReference,
  WidgetSearch,
  WidgetPassageLinks,
  WidgetPassageExports,
  WidgetTextMode,
  WidgetTextSize,
  WidgetHighlight,
  WidgetMorpheus,
  WidgetWordList,
  WidgetTokenList,
  WidgetTextWidth,
  'widget-new-alexandria-commentary': WidgetNewAlexandriaCommentary,
};

export default {
  name: 'Reader',
  components: {
    Skeleton,
    PassageHumanReference,
    PassageRenderText,
    PassageRedirectNotice,
    VersionSelector,
    ...widgets,
  },
  mixins: [
    ReaderNavigationMixin,
  ],
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
      const { versions } = this.$store.state.reader;
      return versions && Object.keys(versions.collections).map(key => versions.collections[key]);
    },
    canSelectVersions() {
      return !this.rightPassage && this.versions && this.versions.length > 1;
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
    lowerText() {
      return this.$store.state.reader.lowerText;
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
    lowerPassage() {
      return this.$store.state.reader.lowerPassage;
    },
    leftPassageText() {
      return this.$store.state.reader.leftPassageText;
    },
    rightPassageText() {
      return this.$store.state.reader.rightPassageText;
    },
    lowerPassageText() {
      return this.$store.state.reader.lowerPassageText;
    },
    leftUrn() {
      return new URN(this.$route.params.leftUrn);
    },
    rightUrn() {
      const { right } = this.$route.query;
      if (!right) {
        return null;
      }
      return this.leftUrn.replace({ version: right });
    },
    lowerUrn() {
      const { lower } = this.$route.query;
      if (!lower) {
        return null;
      }
      return new URN(lower);
    }
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
      const { leftUrn, rightUrn, lowerUrn } = this;
      const { query } = this.$route;
      return this.$store.dispatch(`reader/${constants.READER_LOAD}`, { leftUrn, rightUrn, lowerUrn, query, initial });
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
