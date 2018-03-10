<template>
  <widget class="passage-links">
    <span slot="header">CTS URN</span>
    <div slot="body">
      <template v-if="rightPassage">
        <p><span class="side">L</span> <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${rightPassage.urn}`">{{ leftPassage.urn.toString() }}</a></tt></p>
        <p><span class="side">R</span> <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${rightPassage.urn}`">{{ rightPassage.urn.toString() }}</a></tt></p>
      </template>
      <template v-else>
        <p><tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${passage.urn}`">{{ passage.urn.toString() }}</a></tt></p>
      </template>
    </div>
  </widget>
</template>

<script>
import store from '../../store';
import widget from '../widget';

export default {
  store,
  data() {
    return {
      ctsApiUrl: 'https://scaife-cts.perseus.org/api/cts',
    };
  },
  computed: {
    passage() {
      return this.$store.getters['reader/passage'];
    },
    leftPassage() {
      return this.$store.state.reader.leftPassage;
    },
    rightPassage() {
      return this.$store.state.reader.rightPassage;
    },
  },
  components: {
    widget,
  },
};
</script>
