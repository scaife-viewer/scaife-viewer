<template>
  <div class="toc-list">
    <template v-if="loading">
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <div v-else>
      <div v-for="entry in toc">
        <h2><a :href="entry.reader_url">{{ entry.label }} {{ entry.num }}</a></h2>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../store';

export default {
  store,
  created() {
    this.loading = true;
    this.$store.dispatch('loadToc', document.location.href).then(() => {
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
