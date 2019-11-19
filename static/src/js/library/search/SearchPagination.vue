<template>
  <div class="search-pagination">
    <div>
      Showing <b>{{ startIndex }}</b>&ndash;<b>{{ endIndex }}</b> of <b>{{ totalResults }}</b>
    </div>
    <!-- previous -->
    <div>
      <span v-if="hasPrev">
        <span v-on:click="handleSearch(1)">
          <i class="fa fa-step-backward" style="cursor:pointer;color:#B45141;"></i>
        </span>
        <span v-on:click="handleSearch(pageNum - 1)">
          <i class="fa fa-backward" style="cursor:pointer;color:#B45141;"></i>
        </span>
      </span>
      <span v-else>
        <span class="text-muted"><i class="fa fa-step-backward"></i></span>
        <span class="text-muted"><i class="fa fa-backward"></i></span>
      </span>
      <!-- current -->
      <span class="current">
        page <b>{{ pageNum }}</b> of <b>{{ totalPages }}</b>
      </span>
      <!-- next -->
      <span v-if="hasNext">
        <span v-on:click="handleSearch(pageNum + 1)">
          <i class="fa fa-forward" style="cursor:pointer;color:#B45141;"></i>
        </span>
        <span v-on:click="handleSearch(totalPages)">
          <i class="fa fa-step-forward" style="cursor:pointer;color:#B45141;"></i>
        </span>
      </span>
      <span v-else>
        <span class="text-muted"><i class="fa fa-forward"></i></span>
        <span class="text-muted"><i class="fa fa-step-forward"></i></span>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'search-pagination',
  props: [
    'startIndex', 'endIndex', 'totalResults', 'pageNum',
    'totalPages', 'hasPrev', 'hasNext', 'handleSearch'
  ],
};
</script>
