<template>
  <div :class="['text-group', { open : open || filtered }]">
    <h4>
      <div class="toggle">
        <span class="open-toggle" v-if="!filtered" @click.prevent="toggle">
          <icon name="chevron-down" v-if="open"></icon>
          <icon name="chevron-right" v-else></icon>
        </span>
      </div>
      <div class="label">
        <a :href="getLibraryURL(textGroup)">{{ textGroup.label }}</a>
      </div>
      <div class="urn">
        <span>{{ textGroup.urn }}</span>
      </div>
    </h4>
    <div class="works" v-if="open || filtered">
      <div v-for="work in textGroup.works" class="work" :key="work.urn">
        <div class="filler">&nbsp;</div>
        <div class="label">
          <a :href="getLibraryURL(work)">{{ work.label }}</a>
        </div>
        <div class="urn">{{ work.urn }}</div>
        <div class="versions">
          <TextVersion v-for="text in getTexts(work)" :key="text.urn" :text="text" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TextVersion from './TextVersion.vue';

export default {
  components: { TextVersion },
  props: ["textGroup", "filtered", "texts"],
  data() {
    return {
      open: false
    };
  },
  methods: {
    toggle() {
      this.open = !this.open;
    },
    safeURN(urn) {
      // @@@ maintain backwards compatability
      return urn.endsWith(':') ? urn.slice(0, -1) : urn;
    },
    getLibraryURL(ctsObj) {
      return `/library/${this.safeURN(ctsObj.urn)}/`;
    },
    getTexts(work) {
      const workUrn = this.safeURN(work.urn);
      return this.texts ? this.texts.filter(version => version.urn.startsWith(workUrn)) : this.texts;
    },
  },
};
</script>
