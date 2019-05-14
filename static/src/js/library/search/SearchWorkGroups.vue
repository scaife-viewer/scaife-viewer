<template>
  <div class="search-work-groups">
    <!-- hidden on sm and xs -->
    <div class="d-none d-md-block">
      <h5 v-if="showClearWorkGroup">
        <span>Work Groups</span>
        &nbsp;
        <small class="link-text clear-btn" @click="handleClear()">clear</small>
      </h5>
      <h5 v-if="!showClearWorkGroup">Work Groups</h5>
      <div class="list-group">
        <a
          v-if="!seeMore"
          v-for="work in firstTenWorkGroups"
          :key="work.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, 0, work.text_group.urn)"
        >
          <span>{{ work.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ work.count }}</span>
        </a>
        <a
          v-if="seeMore"
          v-for="work in allworkGroups"
          :key="work.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, 0, work.text_group.urn)"
        >
          <span>{{ work.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ work.count }}</span>
        </a>
        <div class="link-container">
          <small>
            <span v-if="!seeMore && !showClearWorkGroup && showSeeMore" class="link-text" @click="toggleWorkGroups()">
              <span><i class="fas fa-chevron-down"></i></span>
              &nbsp;See More
            </span>
            <span v-if="seeMore && !showClearWorkGroup && showSeeMore" class="link-text" @click="toggleWorkGroups()">
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
        <span>Work Groups</span>
          <span @click="handleShowWorkGroupsChange" v-show="!showWorkGroups">
            <i class="far fa-caret-square-down link-text"></i>
          </span>
          <span @click="handleShowWorkGroupsChange" v-show="showWorkGroups">
            <i class="far fa-caret-square-up link-text"></i>
          </span>
        <small class="link-text"  @click="handleClear()" v-if="showClearWorkGroup">&nbsp;clear</small>
      </h5>
      <div class="list-group" :style="{'display':showWorkGroups?'block':'none'}">
        <a
          v-for="work in firstTenWorkGroups"
          :key="work.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, 0, work.text_group.urn)"
        >
          <span>{{ work.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ work.count }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'search-work-groups',
  props: [
    'handleSearch', 'workGroups', 'showClearWorkGroup', 'showWorkGroups',
    'handleShowWorkGroupsChange', 'textGroup',
  ],
  data() {
    return {
      seeMore: false,
      showSeeMore: true,
    }
  },
  computed: {
    allworkGroups() {
      return this.workGroups;
    },
    firstTenWorkGroups() {
      this.showSeeMore = false;
      if ((this.workGroups).length >= 10) {
        this.showSeeMore = true;
      }
      return this.workGroups.slice(0, 10);
    },
  },
  methods: {
    toggleWorkGroups() {
      this.seeMore = !this.seeMore;
    },
    handleClear() {
      this.handleSearch(0, this.textGroup);
    }
  },
};
</script>
