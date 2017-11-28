<template>
  <div class="widget">
    <h2>CTS URN</h2>
    <p>
      <tt><a :href="`https://perseus-cts.eu1.eldarioncloud.com/api/cts?request=GetPassage&amp;urn=${passage.urn}`">{{ passage.urn }}</a></tt>
    </p>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import store from '../../../store';

export default {
  store,
  computed: {
    ...mapState({
      passage: state => state.reader.passage,
    }),
  },
};
</script>
