<template>
  <reader v-if="passage">
    <div class="passage-heading">
      <a href="/">Library &gt;</a>
      <h1><a v-for="breadcrumb in passage.text.ancestors" :key="breadcrumb.urn" :href="breadcrumb.url">{{ breadcrumb.label }}</a></h1>
      <h3><passage-human-reference :passage="passage"></passage-human-reference></h3>
    </div>
    <div id="overall" class="overall" :dir="passage.rtl ? 'rtl' : 'ltr'">
      <template v-if="loaded">
        <div class="pg-left">
          <a v-if="passage.prev" href="#" @click.prevent="setPassage(passage.prev.urn)"><span><i :class="['fa', {'fa-chevron-left': !passage.rtl, 'fa-chevron-right': passage.rtl}]"></i></span></a>
        </div>
        <passage-render-text :passage="passage"></passage-render-text>
        <div class="pg-right">
          <a v-if="passage.next" href="#" @click.prevent="setPassage(passage.next.urn)"><span><i :class="['fa', {'fa-chevron-left': passage.rtl, 'fa-chevron-right': !passage.rtl}]"></i></span></a>
        </div>
      </template>
    </div>
  </reader>
</template>

<script>
import { mapState } from 'vuex';
import store from '../../store';
import Reader from './Reader';
import PassageRenderText from './PassageRenderText';
import PassageHumanReference from './PassageHumanReference';

export default {
  store,
  props: {
    urn: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.setPassage(this.urn).then(() => {
      this.loaded = true;
    });
  },
  data() {
    return {
      loaded: false,
    };
  },
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
    }),
  },
  methods: {
    setPassage(urn) {
      return this.$store.dispatch('setPassage', urn);
    },
  },
  components: {
    Reader,
    PassageRenderText,
    PassageHumanReference,
  },
};
</script>
