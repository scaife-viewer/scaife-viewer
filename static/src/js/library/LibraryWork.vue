<template>
  <div class="work" :key="work.urn">
    <div class="label">
      <a :href="getLibraryURL(work)">{{ work.label }}</a>
    </div>
    <div class="text-group">
      {{ textGroup.label }}
    </div>
    <div class="urn">
      {{ work.urn }}
    </div>
    <div class="versions">
      <TextVersion v-for="text in getTexts(work)" :key="text.urn" :text="text" />
    </div>
  </div>
</template>

<script>
import TextVersion from './TextVersion.vue';

export default {
  props: ['work', 'filtered', 'text-groups', 'versions'],
  components: { TextVersion },
  computed: {
    textGroup() {
      // @@@ .includes
      // @@@ .find
      return this.textGroups.find((textGroup) => {
        return this.work.urn.includes(this.safeURN(textGroup.urn));
      });
    },
  },
  methods: {
    safeURN(urn) {
      // @@@ maintain backwards compatability
      return urn.endsWith(':') ? urn.slice(0, -1) : urn;
    },
    getTexts(work) {
      const workUrn = this.safeURN(work.urn);
      return this.versions ? this.versions.filter(version => version.urn.startsWith(workUrn)) : this.versions;
    },
    getLibraryURL(ctsObj) {
      return `/library/${this.safeURN(ctsObj.urn)}/`;
    },
  },
};
</script>
