<template>
  <section>
    <div class="search-results-format">
      <h5>Results Format</h5>
      <div class="form-check">
        <input
          type="radio"
          id="type-instances"
          name="instances"
          :value="searchResultsType"
          @input="handleResultsTypeChange"
          :checked="searchResultsType=='instances'"
          class="form-check-input"
        >
        <label class="form-check-label" for="type-instances">Instances</label>
      </div>
        <div class="form-check">
        <input
          type="radio"
          id="type-passages"
          name="passages"
          :value="searchResultsType"
          @input="handleResultsTypeChange"
          :checked="searchResultsType=='passages'"
          class="form-check-input"
        >
        <label class="form-check-label" for="type-passages">Passages</label>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'search-results-format',
  props: ['searchResultsType', 'handleResultsTypeChange'],
};
</script>
