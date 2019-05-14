<template>
  <div class="search-works">
    <!-- hidden on sm and xs -->
    <div class="d-none d-md-block">
      <h5 v-if="showClearWork">
        <span>Works</span>
        &nbsp;
        <small class="link-text clear-btn" @click="handleClear()">clear</small>
      </h5>
      <h5 v-if="!showClearWork">Works</h5>
      <div class="list-group">
        <a
          v-if="!seeMore"
          v-for="work in firstTenWorks"
          :key="work.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, 0, work.text_group.urn)"
        >
          <span>{{ work.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ work.count }}</span>
        </a>
        <a
          v-if="seeMore"
          v-for="work in allworks"
          :key="work.text_group.urn"
          class="list-group-item d-flex justify-content-between align-items-center link-text"
          @click="handleSearch(1, 0, work.text_group.urn)"
        >
          <span>{{ work.text_group.label }}</span>
          <span class="badge badge-primary badge-pill">{{ work.count }}</span>
        </a>
        <div class="link-container">
          <small>
            <span v-if="!seeMore && !showClearWork && showSeeMore" class="link-text" @click="toggleWorks()">
              <span><i class="fas fa-chevron-down"></i></span>
              &nbsp;See More
            </span>
            <span v-if="seeMore && !showClearWork && showSeeMore" class="link-text" @click="toggleWorks()">
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
        <span>Works</span>
          <span @click="handleShowWorksChange" v-show="!showWorks">
            <i class="far fa-caret-square-down link-text"></i>
          </span>
          <span @click="handleShowWorksChange" v-show="showWorks">
            <i class="far fa-caret-square-up link-text"></i>
          </span>
        <small class="link-text"  @click="handleClear()" v-if="showClearWork">&nbsp;clear</small>
      </h5>
      <div class="list-group" :style="{'display':showWorks?'block':'none'}">
        <a
          v-for="work in firstTenWorks"
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
  name: 'search-works',
  props: [
    'handleSearch', 'works', 'showClearWork', 'showWorks',
    'handleShowWorksChange', 'textGroup',
  ],
  data() {
    return {
      seeMore: false,
      showSeeMore: true,
    }
  },
  computed: {
    allworks() {
      return this.works;
    },
    firstTenWorks() {
      this.showSeeMore = false;
      if ((this.works).length >= 10) {
        this.showSeeMore = true;
      }
      return this.works.slice(0, 10);
    },
  },
  methods: {
    toggleWorks() {
      this.seeMore = !this.seeMore;
    },
    handleClear() {
      this.handleSearch(0, this.textGroup);
    }
  },
};
</script>
