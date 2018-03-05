<template>
  <widget class="chs-commentary" v-if="show">
    <span slot="header">CHS Commentary</span>
    <div slot="body">
      <p class="no-comment" v-if="!comments || comments.length === 0">
        No comments found.
      </p>
      <div v-else>
        <div v-for="comment in comments" :key="comment._id" class="comment">
          <h6>{{ comment.latestRevision.title }}</h6>
          <div class="commenter-name">{{ comment.commenters[0].name }}</div>
          <div class="comment-text" v-html="comment.latestRevision.text"></div>
        </div>
      </div>
    </div>
  </widget>
</template>

<script>
import qs from 'query-string';
import store from '../../store';
import widget from '../widget';

export default {
  store,
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
  },
  data() {
    return {
      show: false,
      comments: [],
    };
  },
  mounted() {
    this.fetchCommentary();
  },
  watch: {
    passage: {
      handler: 'fetchCommentary',
      immediate: true,
    },
  },
  methods: {
    async fetchCommentary() {
      const apiUrl = 'http://commentary.chs.orphe.us/graphql';
      const { urn } = this.passage;
      const query = `{ commentsOn(urn: "${urn}") { _id updated latestRevision { title text } commenters { _id name } } }`;
      const params = qs.stringify({ query });
      const res = await fetch(`${apiUrl}?${params}`);
      if (!res.ok) {
        if (res.status === 404) {
          this.show = false;
          return;
        }
        throw new Error(res.status);
      }
      if (this.show === false) {
        this.show = true;
      }
      const data = await res.json();
      this.comments = data.data.commentsOn;
    },
  },
  components: {
    widget,
  },
};
</script>
