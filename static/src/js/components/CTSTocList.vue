<template>
  <div class="toc-list">
    <template v-if="loading">
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <div v-else>
      <div v-for="entry in toc" :key="entry.urn">
        <h2><a :href="entry.url">{{ entry.label }} {{ entry.num }}</a></h2>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../store';

export default {
  store,
  props: ['textUrl'],
  created() {
    this.loading = true;
    this.$store.dispatch('loadTocList', this.textUrl).then(() => {
      this.loading = false;
    });
  },
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapState({
      toc: state => state.library.toc,
    }),
  },
};
</script>
