<template>
  <section>
    <div
      :class="[searchResultsType==='instances' ? 'result' : 'result-passages']"
      v-if="!secondLoading"
      v-for="result in results" :key="result.passage.url"
    >
      <div class="passage-heading">
        <h2>
          <a :href="createPassageLink(result.passage.url)">
            <span v-for="breadcrumb in result.passage.text.ancestors" :key="breadcrumb.label">
              {{ breadcrumb.label }},
            </span>
            <span>{{ result.passage.refs.start.human_reference }}</span>
            <span v-if="result.passage.refs.end">
              to {{ result.passage.refs.end.human_reference }}
            </span>
            <span v-if="!result.passage.refs.end">
              ({{ result.passage.refs.start.reference }})
            </span>
            <span v-if="result.passage.refs.end">
              ({{ result.passage.refs.start.reference }} to &ndash; {{ result.passage.refs.end.reference }})
            </span>
          </a>
          <span class="badge badge-light">{{ result.passage.text.kind }}</span>
        </h2>
      </div>
      <div v-if="searchResultsType==='instances'" class="content">
        <p v-for="result in result.content" :key="result">
          <span v-html="result"></span>
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'search-results',
  props: ['secondLoading', 'results', 'createPassageLink', 'searchResultsType'],
};
</script>
