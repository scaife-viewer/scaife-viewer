<template>
  <div class="search-text-groups">
    <!-- hidden on sm and xs -->
    <div class="d-none d-md-block">
      <h5 v-if="showClearTextGroup">
        <span>Text Groups</span>
        &nbsp;
        <small class="link-text clear-btn" @click="handleClear()">clear</small>
      </h5>
      <h5 v-if="!showClearTextGroup">Text Groups</h5>
      <div class="list-group">
        <a
          v-if="!seeMore"
          v-for="ftg in firstFiveTextGroups"
          :key="ftg.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, ftg.text_group.urn)"
        >
          <span>{{ ftg.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ ftg.count }}</span>
        </a>
        <a
          v-if="seeMore"
          v-for="ftg in allTextGroups"
          :key="ftg.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, ftg.text_group.urn)"
        >
          <span>{{ ftg.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ ftg.count }}</span>
        </a>
        <div class="link-container">
          <small>
            <span v-if="!seeMore && !showClearTextGroup && showSeeMore" class="link-text" @click="toggleTextGroups()">
              <span><i class="fas fa-chevron-down"></i></span>
              &nbsp;See More
            </span>
            <span v-if="seeMore && !showClearTextGroup && showSeeMore" class="link-text" @click="toggleTextGroups()">
              <span><i class="fas fa-chevron-up"></i></span>
              &nbsp;See Less
            </span>
          </small>
        </div>
      </div>
    </div>
    <!-- visible on sm and xs -->
    <div class="d-md-none">
      <h5>
        <span>Text Groups</span>
          <span @click="handleShowTextGroupsChange" v-show="!showTextGroups">
            <i class="far fa-caret-square-down link-text"></i>
          </span>
          <span @click="handleShowTextGroupsChange" v-show="showTextGroups">
            <i class="far fa-caret-square-up link-text"></i>
          </span>
        <small class="link-text" @click="handleClear()" v-if="showClearTextGroup">&nbsp;clear</small>
      </h5>
      <div class="list-group" :style="{'display':showTextGroups?'block':'none'}">
        <a
          v-for="ftg in firstFiveTextGroups"
          :key="ftg.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, ftg.text_group.urn)"
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
    'handleSearch', 'textGroups', 'showClearTextGroup', 'showTextGroups',
    'handleShowTextGroupsChange', 'clearWorks',
  ],
  data() {
    return {
      seeMore: false,
      showSeeMore: true,
    }
  },
  computed: {
    allTextGroups() {
      return this.textGroups;
    },
    firstFiveTextGroups() {
      this.showSeeMore = false;
      if ((this.textGroups).length >= 5) {
        this.showSeeMore = true;
      }
      return this.textGroups.slice(0, 5);
    },
  },
  methods: {
    toggleTextGroups() {
      this.seeMore = !this.seeMore;
    },
    handleClear() {
      this.handleSearch(0, 0, 0);
      this.clearWorks();
    }
  },
};
</script>
