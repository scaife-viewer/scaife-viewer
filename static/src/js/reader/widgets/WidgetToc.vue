<template>
  <base-widget>
    <span slot="header">Table of Contents</span>
    <div slot="body">
      <div class="lookahead-container u-flex">
        <div class="form-group mb-1">
          <div class="input-group u-flex">
            <input
                class="form-control form-control-sm"
                v-model="query"
                placeholder="Filter this table of contents... (e.g. Book 3)"
            />
            <div
              class="input-group-append"
              v-if="query"
            >
              <button class="btn btn-outline-secondary btn-sm" type="button" @click="clearQuery">
                <icon name="times"></icon>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="paginated.length">
        <ul class="list-group list-group-flush list-group-sm">
          <li
            v-for="(item, idx) in paginated"
            :key="idx"
            :class="listItemClasses(item)"
          >
            <router-link :to="getRouterLink(item)">
              {{ item.label + ' ' + item.num }}
            </router-link>
          </li>
        </ul>
      </div>
      <p class="u-legend" v-else>No results.</p>

      <nav class="mt-2" v-if="totalPages > 1">
        <ul class="pagination pagination-sm justify-content-center">
          <li
              :class="['page-item', currentPage === 1 ? 'disabled' : '']"
          >
            <a class="page-link" href="#" aria-label="Previous"
              @click="changePage(currentPage - 1)"
            >
              <span aria-hidden="true">&laquo;</span>
              <span class="sr-only">Previous</span>
            </a>
          </li>
          <li
              :class="['page-item', page === currentPage ? 'active' : '']"
              v-for="page in pages" :key="page"
          >
            <a class="page-link" href="#" @click="changePage(page)">{{ page }}</a>
          </li>
          <li
              :class="['page-item', currentPage === totalPages ? 'disabled' : '']"
          >
            <a class="page-link" href="#" aria-label="Next"
              @click="changePage(currentPage + 1)"
            >
              <span aria-hidden="true">&raquo;</span>
              <span class="sr-only">Next</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </base-widget>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: 'widget-toc',
  data() {
    return {
      query: '',
      itemsPerPage: 12,
      currentPage: 1,
    }
  },
  computed: {
    ...mapGetters('reader', ['textToc']),
    filtered() {
      if (!this.query) {
        return this.textToc;
      }

      const lenses = { getItem: obj => obj.label + ' ' + obj.num };
      return this.textToc.filter(obj =>
          Object.values(lenses)
              .map(lens =>
                  lens(obj)
                      .toLowerCase()
                      .includes(this.query.toLowerCase())
              )
              .some(Boolean)
      );
    },
    paginated() {
      const startIndex = (this.currentPage - 1) * this.itemsPerPage;
      const endIndex = startIndex + this.itemsPerPage;

      return this.filtered.slice(startIndex, endIndex);
    },
    pages() {
      const maxDisplayedPages = 5;
      const halfMaxDisplayedPages = Math.floor(maxDisplayedPages / 2);

      let startPage = Math.max(this.currentPage - halfMaxDisplayedPages, 1);
      const endPage = Math.min(startPage + maxDisplayedPages - 1, this.totalPages);

      if (endPage - startPage + 1 < maxDisplayedPages) {
        startPage = Math.max(endPage - maxDisplayedPages + 1, 1);
      }

      const pages = [];
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      return pages;
    },
    totalPages() {
      return Math.ceil(this.filtered.length / this.itemsPerPage);
    }
  },
  watch: {
    filtered() {
      this.currentPage = 1;
    }
  },
  methods: {
    clearQuery() {
      this.query = '';
      this.currentPage = 1;
    },
    changePage(page) {
      this.currentPage = page;
    },
    getRouterLink(item) {
      return {
        name: 'reader',
        params: { leftUrn: item.urn.toString() },
        query: this.$route.query
      };
    },
    listItemClasses(item) {
      return ['list-group-item', item.urn === this.$route.params.leftUrn ? 'active' : ''];
    }
  }
};
</script>

<style scoped>
.lookahead-container {
  align-items: center;
  margin-bottom: 0.12em;
  .form-group {
    width: 95%;
  }
}
li.list-group-item {
  padding-top: 0;
  padding-bottom: 0.0px;
  border-bottom-width: 0;
}

li.list-group-item.active > a {
  color: white;
}
</style>