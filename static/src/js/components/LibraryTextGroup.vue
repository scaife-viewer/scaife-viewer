<template>
  <div :class="['text-group', { open : open || filtered }]">
    <h4>
      <div class="toggle">
        <span class="open-toggle" v-if="!filtered" @click.prevent="toggle">
          <i :class="['fa', open ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
        </span>
      </div>
      <div class="label">
        <a :href="textGroup.url">{{ textGroup.label }}</a>
      </div>
      <div class="urn">
        <span>{{ textGroup.urn }}</span>
      </div>
    </h4>
    <div class="works" v-if="open || filtered">
      <div v-for="work in textGroup.works" class="work" :key="work.urn">
        <div class="filler">&nbsp;</div>
        <div class="label">
          <a :href="work.url">{{ work.label }}</a>
        </div>
        <div class="urn">
          {{ work.urn }}
        </div>
        <div class="versions">
          <template v-for="text in work.texts">
            <a :key="text.urn" :href="text.reader_url" class="badge badge-light" v-popover:bottom="{title: text.label, content: text.description, trigger: 'hover'}">
              {{ text.lang }}
            </a>{{ ' ' }}
          </template>
        </div>
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
