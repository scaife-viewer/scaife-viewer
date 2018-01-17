<template>
  <div class="text-group">
    <h4>
      <span v-if="!filtered" @click.prevent="toggle">
        <span class="open-toggle">
          <i :class="['fa', open ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
        </span>
      </span>
      <a :href="textGroup.url">{{ textGroup.label }}</a>
    </h4>
    <div v-if="open || filtered" v-for="work in textGroup.works" class="row" :key="work.urn">
      <div class="col">
        <a :href="work.url">{{ work.label }}</a>
      </div>
      <div class="col">
        {{ work.urn }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['textGroup', 'filtered'],
  data() {
    return {
      open: false,
    };
  },
  methods: {
    toggle() {
      this.open = !this.open;
    },
  },
};
</script>
