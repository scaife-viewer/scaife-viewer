<template>
  <div :class="['text', `text-${textSize}`]">
    <text-loading v-if="loading"></text-loading>
    <component :class="{'text-loading': loading, 'text-loaded': !loading}" :is="renderedText"></component>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../../store';
import TextPart from './TextPart';
import TextLoading from './TextLoading';

export default {
  store,
  props: ['passage', 'loading'],
  computed: {
    ...mapState({
      textSize: state => state.reader.textSize,
    }),
    renderedText() {
      return {
        store,
        template: this.passage.text_html,
        components: {
          TextPart,
        },
      };
    },
  },
  components: {
    TextLoading,
  },
};
</script>
