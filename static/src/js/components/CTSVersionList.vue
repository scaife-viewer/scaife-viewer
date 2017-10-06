<template>
  <div class="version-list">
    <template v-if="loading">
      <div class="text-center">
        <i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>
      </div>
    </template>
    <div v-else>
      <div v-for="group in versions.groups">
        <h2>{{ versions.group_name }} {{ group.num }}</h2>
        <ul>
          <li v-for="range in group.ranges"><a :href="range.url">{{ range.start }}<template v-if="range.end">&ndash;{{ range.end }}</template></a></li>
        </ul>
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
    this.$store.dispatch('loadVersions', document.location.href).then(() => {
      this.loading = false;
    });
  },
  data() {
    return {
      loading: false,
    };
  },
  computed: mapState(['versions']),
};
</script>
