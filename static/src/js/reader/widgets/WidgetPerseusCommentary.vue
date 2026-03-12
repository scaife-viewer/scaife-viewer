<template>
  <base-widget class="perseus-commentary" v-if="(entries || []).length > 0">
    <span slot="header">Perseus Commentary</span>
    <div slot="body">
      <div
        v-for="entry in entries"
        class="commentary-entry"
        :key="entry.id"
        :id="entry.urn"
        :corresp="entry.corresp"
      >
        <span class="commentary-entry-citation"
          >{{
            entry.corresp
              .split(":")
              .at(-1)
              .replace(/@.*/, "")
          }}. {{ entry.lemma }}
        </span><div class="commentary-entry-content" v-html="entry.content" />
      </div>
      <div v-if="totalPages > 1">
        <a
          v-on:click="previousPage"
          :style="{ cursor: currentPage - 1 > 0 ? 'pointer' : 'auto' }"
        >
          <span class="text-muted"><i class="fa fa-chevron-left"></i></span>
        </a>
        <a
          v-on:click="nextPage"
          :style="{ cursor: currentPage + 1 < totalPages ? 'pointer' : 'auto' }"
        >
          <span class="text-muted"><i class="fa fa-chevron-right"></i></span>
        </a>
      </div>
    </div>
  </base-widget>
</template>

<script>
import api from "../../api";
import constants from "../../constants";

const debounce = require("lodash.debounce");

export default {
  name: "widget-perseus-commentary",
  computed: {
    entries() {
      return this.$store.state.reader.perseusCommentaries.results;
    },
    currentPage() {
      return this.$store.state.reader.perseusCommentaries.current_page;
    },
    totalPages() {
      return this.$store.state.reader.perseusCommentaries.total_pages;
    },
  },
  methods: {
    nextPage: debounce(function _nextPage() {
      if (this.currentPage + 1 > this.totalPages) {
        return;
      }

      api.getPerseusCommentaryEntries(
        this.$store.state.reader.leftText.urn.toString(),
        { page: this.currentPage + 1 },
        (data) => {
          this.$store.commit(`reader/${constants.SET_PERSEUS_COMMENTARY_ENTRIES}`, data);
        },
      );
    }, 250),
    previousPage: debounce(function _previousPage() {
      if (this.currentPage - 1 <= 0) {
        return;
      }

      api.getPerseusCommentaryEntries(
        this.$store.state.reader.leftText.urn.toString(),
        { q: this.query, page: this.currentPage - 1 },
        (data) => {
          this.$store.commit(`reader/${constants.SET_PERSEUS_COMMENTARY_ENTRIES}`, data);
        },
      );
    }, 250),
  },
};
</script>

<style>
gloss {
  white-space: pre-wrap;
}

lem {
  font-weight: bold;
}

s {
  text-decoration: none;
}

.commentary-entry {
  margin-top: 0.5rem;
}

.commentary-entry-citation {
  float: left;
  font-weight: bold;
}
</style>
