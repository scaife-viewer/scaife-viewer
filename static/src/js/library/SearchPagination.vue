<template>
  <div class="search-pagination">
    <div>
      Showing <b>{{ start_index }}</b>&ndash;<b>{{ end_index }}</b> of <b>{{ total_results }}</b>
    </div>
    <!-- previous -->
    <div>
      <span v-if="page_num > 1">
        <a href="#"><i class="fa fa-step-backward"></i></a>
        <span v-on:click="showNextPrevPage('prev')">
          <i class="fa fa-backward" style="cursor:pointer;color:#B45141;"></i>
        </span>
      </span>
      <span v-else>
        <span class="text-muted"><i class="fa fa-step-backward"></i></span>
        <span class="text-muted"><i class="fa fa-backward"></i></span>
      </span>
      <!-- current -->
      <span class="current">
        page <b>{{ page_num }}</b> of <b>{{ total_pages }}</b>
      </span>
      <!-- next -->
      <span v-if="page_num + 1 <= total_pages">
        <span v-on:click="showNextPrevPage('next')">
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
  props: ['start_index', 'end_index', 'total_results', 'page_num', 'total_pages', 'showNextPrevPage'],
};
</script>
