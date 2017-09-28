<template>
  <div id="resources">
    <template v-if="loading">
      <i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>
    </template>
    <template v-else>
      <div class="input-group">
        <input
          type="text"
          class="form-control"
          v-model="query"
          placeholder="Type to filter the resources..."
        >
        <span class="input-group-addon" v-if="filtered">
          <i class="fa fa-times" @click="clearFilter"></i>
        </span>
      </div>
      <table class="table">
        <tr v-for="resource in filteredResources" :key="resource.url">
          <td><a :href="resource.url">{{ resource.label }}</a></td>
        </tr>
      </table>
    </template>
  </div>
</template>

<script>
const debounce = require('lodash.debounce');

export default {
  created() {
    this.loading = true;
    this.loadResources().then((resources) => {
      this.resources = resources;
      this.filteredResources = Object.assign({}, resources);
      this.loading = false;
    });
  },
  data() {
    return {
      loading: true,
      query: '',
      resources: null,
      filteredResources: null,
      filtered: false,
    };
  },
  watch: {
    query() {
      this.filterResources();
    },
  },
  methods: {
    loadResources() {
      return fetch(document.location.href, {
        headers: {
          Accept: 'application/json',
        },
      }).then((response) => {
        return response.json().then((data) => {
          return data.object;
        });
      });
    },
    clearFilter() {
      this.query = '';
      this.filteredResources = Object.assign({}, this.resources);
      this.filtered = false;
    },
    filterResources: debounce(
      function f() {
        const query = this.query.trim();
        if (query === '') {
          this.clearFilter();
          return;
        }
        const r = [];
        this.resources.forEach((resource) => {
          if (resource.label.toLowerCase().indexOf(query.toLowerCase()) !== -1) {
            r.push(resource);
          }
        });
        this.filteredResources = r;
        this.filtered = true;
      },
      250,
    ),
  },
};
</script>
