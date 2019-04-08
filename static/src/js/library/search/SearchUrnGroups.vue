<template>
  <div>
    <!-- hidden on sm and xs -->
    <div>
      <br>
      <h5>URN Groups</h5>
      <div class="list-group" :style="{'display':urnGroups?'block':'none'}">
        <a
          v-for="(value, key) in urnGroups"
          :key="key"
          class="list-group-item d-flex justify-content-between align-items-center"
          style="cursor:pointer;color:#B45141;"
          v-on:click="handleSearch(1, key.split('.')[0], key.split('.')[1])"
        >
          <span>{{ value.label }}</span>
          <span class="badge badge-primary badge-pill">{{ value.count }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'search-urn-groups',
  props: [
    'urnGroups', 'handleSearch'
  ],
};
</script>
