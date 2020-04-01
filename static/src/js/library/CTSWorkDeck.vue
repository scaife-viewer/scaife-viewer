<template>
  <div class="work">
    <h3><a :href="libraryURL"><b>{{ work.label }}</b></a></h3>
    <div class="card-deck">
      <CTSWorkCard
        v-for="text in texts"
        :key="text.urn"
        :text="text"
      />
    </div>
  </div>
</template>

<script>
  import { safeURN } from '../urn';
  import CTSWorkCard from './CTSWorkCard.vue';

  export default {
    props: ['work', 'versions'],
    components: { CTSWorkCard },
    computed: {
      libraryURL() {
        return `/library/${safeURN(this.work.urn)}/`;
      },
      texts() {
        const workUrn = safeURN(this.work.urn);
        return this.versions ? this.versions.filter(version => version.urn.startsWith(workUrn)) : this.versions;
      },
    }
  }
</script>
