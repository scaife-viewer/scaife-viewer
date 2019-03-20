<template>
  <div class="search-pagination">
    <div>
      Showing <b>{{ startIndex }}</b>&ndash;<b>{{ endIndex }}</b> of <b>{{ totalResults }}</b>
    </div>
    <!-- previous -->
    <div>
      <span v-if="hasPrev">
        <a href="#"><i class="fa fa-step-backward"></i></a>
        <span v-on:click="handlePrevNext(pageNum - 1)">
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
        <span v-on:click="handlePrevNext(pageNum + 1)">
          <i class="fa fa-forward" style="cursor:pointer;color:#B45141;"></i>
        </span>
        <a href="#"><i class="fa fa-step-forward"></i></a>
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
  props: [
    'startIndex', 'endIndex', 'totalResults', 'pageNum',
    'totalPages', 'hasPrev', 'hasNext', 'handlePrevNext'
  ],
};
</script>
