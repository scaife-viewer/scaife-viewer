<template>
  <section>
    <div class="container">
      <div class="search-guide">
        <h3>Search Guide</h3>
        <div class="row">
          <div class="col-md-6">
            <kbd>+</kbd> signifies AND operation<br>
            <kbd>|</kbd> signifies OR operation<br>
            <kbd>-</kbd> negates a single token<br>
            <kbd>"</kbd> wraps a number of tokens to signify a phrase for searching<br>
          </div>
          <div class="col-md-6">
            <kbd>*</kbd> at the end of a term signifies a prefix query<br>
            <kbd>(</kbd> and <kbd>)</kbd> signify precedence<br>
            <kbd>~<var>num</var></kbd> after a word signifies edit distance (fuzziness)<br>
            <kbd>~<var>num</var></kbd> after a phrase signifies slop amount<br>
          </div>
        </div>
      </div>
      <form class="search-form" v-on:submit.prevent="onSubmit">
        <div class="form-group">
          <input type="text" class="form-control" placeholder="Search..." :value="searchQuery" @input="handleSearchQueryChange">
          <input
            type="radio"
            id="kind-form"
            name="form"
            :value="searchType"
            @input="handleTypeChange"
            :checked="searchType=='form'"
          >
          <label for="kind-form">Form</label>
          <input
            type="radio"
            id="kind-lemma"
            name="lemma"
            :value="searchType"
            @input="handleTypeChange"
            :checked="searchType=='lemma'"
          >
          <label for="kind-lemma">Lemma (Greek only)</label>
        </div>
      </form>
      <!-- <div class="row">
        <div class="col-sm-3">
          {% if page.object_list.filtered_text_groups %}
            <h5>Text Groups{% if request.GET.tg %} <a href="?{% query tg='' p='' %}"><small>clear</small></a>{% endif %}</h5>
            <div class="list-group">
              {% for ftg in page.object_list.filtered_text_groups %}
                <a href="?{% query tg=ftg.text_group.urn p='' %}" class="list-group-item d-flex justify-content-between align-items-center">
                  {{ ftg.text_group.label }}
                  <span class="badge badge-primary badge-pill">{{ ftg.count }}</span>
                </a>
              {% endfor %}
            </div>
          {% endif %}
        </div>
        <div class="col-sm-9">
          {% if error %}
            <div class="alert alert-danger" role="alert">
              DEV ERROR: {{ error.reason }}
              <pre>{{ error.response }}</pre>
            </div>
          {% endif %}
          {% if paginator.count %}
            {% include "_search_pagination.html" %}
            <div>
              {% for result in page.object_list %}
                <div class="result">
                  {% with passage=result.passage %}
                    <div class="passage-heading">
                      <h2>
                        <a href="{{ result.link }}?q={{ q }}&amp;qk={{ kind }}">
                          {% for breadcrumb in passage.text.ancestors %}
                            {{ breadcrumb.label }},
                          {% endfor %}
                          {{ passage.refs.start.human_reference }}{% if passage.refs.end %} to {{ passage.refs.end.human_reference }}{% endif %} ({{ passage.refs.start.reference }}{% if passage.refs.end %} &ndash; {{ passage.refs.end.reference }}{% endif %})
                        </a>
                      </h2>
                    </div>
                  {% endwith %}
                  <div class="content">
                    {% for c in result.content %}
                      <p>{{ c|safe }}</p>
                    {% endfor %}
                  </div>
                </div>
              {% endfor %}
            </div>
            {% include "_search_pagination.html" %}
          {% elif q %}
            <div>No results found for <b>{{ q }}</b>.</div>
          {% endif %}
        </div>
      </div> -->
    </div>
  </section>
</template>

<script>
import constants from '../constants';
import api from '../api';

export default {
  name: 'search-view',
  computed: {
    searchQuery() {
      return this.$store.state.reader.searchQuery;
    },
    searchType() {
      return this.$store.state.reader.searchType;
    },
  },
  methods: {
    handleSearchQueryChange(e) {
      this.$store.commit(`reader/${constants.SET_SEARCH_QUERY}`, { query:  e.target.value });
    },
    handleTypeChange(e) {
      this.$store.commit(`reader/${constants.SET_SEARCH_TYPE}`, { type:  e.target.name });
    },
    onSubmit() {
      const query = this.$store.state.reader.searchQuery;
      if (query !== '') {
        // move to an action
        const params = {
          kind: this.$store.state.reader.searchType,
          q: query
        }
        api.searchText(params, 'search/text/', result => {
          console.log(result)
        });
      }
    }
  },
};
</script>
