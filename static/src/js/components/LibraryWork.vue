<template>
  <div class="work" :key="work.urn">
    <div class="label">
      <a :href="work.url">{{ work.label }}</a>
    </div>
    <div class="text-group">
      {{ work.textGroup.label }}
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
</template>

<script>
export default {
  props: ['work', 'filtered'],
};
</script>
