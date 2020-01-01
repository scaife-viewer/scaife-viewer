<template>
  <div v-if="!loaded">Loading</div>
  <router-view v-else></router-view>
</template>

<script>
import {} from './constants';

export default {
  created() {},
  watch: {},
  computed: {},
  data() {
    return {
      loaded: true
    }
  }
}
</script>
