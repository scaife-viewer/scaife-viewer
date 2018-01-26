<template>
  <widget>
    <span slot="header">CTS URN</span>
    <div slot="body">
      <template v-if="rightPassage">
        <div>Left <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${rightPassage.urn}`">{{ leftPassage.urn.toString() }}</a></tt></div>
        <div>Right <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${rightPassage.urn}`">{{ rightPassage.urn.toString() }}</a></tt></div>
      </template>
      <template v-else>
        <tt><a :href="`${ctsApiUrl}?request=GetPassage&amp;urn=${passage.urn}`">{{ passage.urn.toString() }}</a></tt>
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
      ctsApiUrl: 'https://perseus-cts.eu1.eldarioncloud.com/api/cts',
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
