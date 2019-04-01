<template>
  <div v-if="textGroups.length" class="col-md-3">
    <!-- hidden on sm and xs -->
    <div class="d-none d-md-block">
      <h5 v-if="showClear">
        <span>Text Groups</span>
        &nbsp;
        <small style="cursor:pointer;color:#B45141;" v-on:click="handleSearch(0)">clear</small>
      </h5>
      <h5 v-if="!showClear">Text Groups</h5>
      <div class="list-group">
        <a
          v-for="ftg in textGroups"
          :key="ftg.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center"
          style="cursor:pointer;color:#B45141;"
          v-on:click="handleSearch(1, ftg.text_group.urn)"
        >
          <span>{{ ftg.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ ftg.count }}</span>
        </a>
      </div>
    </div>
    <!-- visible on sm and xs -->
    <div class="d-md-none">
      <h5>
        <span>Text Groups</span>
          <span v-on:click="handleshowTextGroupsChange" v-show="!showTextGroups">
            <i class="far fa-caret-square-down" style="cursor:pointer;color:#B45141;"></i>
          </span>
          <span v-on:click="handleshowTextGroupsChange" v-show="showTextGroups">
            <i class="far fa-caret-square-up" style="cursor:pointer;color:#B45141;"></i>
          </span>
        <small style="cursor:pointer;color:#B45141;" v-on:click="handleSearch(0)" v-if="showClear">&nbsp;clear</small>
      </h5>
      <div class="list-group" :style="{'display':showTextGroups?'block':'none'}">
        <a
          v-for="ftg in textGroups"
          :key="ftg.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center"
          style="cursor:pointer;color:#B45141;"
          v-on:click="handleSearch(1, ftg.text_group.urn)"
        >
          <span>{{ ftg.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ ftg.count }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'search-text-groups',
  props: [
    'handleSearch', 'textGroups', 'showClear', 'showTextGroups', 'handleshowTextGroupsChange'
  ],
};
</script>
