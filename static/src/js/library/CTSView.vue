<template>
    <cts-toc-list v-if="isToc"></cts-toc-list>
    <cts-work-list v-else></cts-work-list>
</template>
<script>
import URN from '../urn';

import CTSTocList from './CTSTocList.vue';
import CTSWorkList from './CTSWorkList.vue';

export default {
    name: 'cts-view',
    components: {
        'cts-toc-list': CTSTocList,
        'cts-work-list': CTSWorkList
    },
    computed: {
        isToc() {
            const urn = new URN(this.$route.params.urn);
            console.log(this.$route.params.urn, urn);
            return urn.work !== null;
        }
    }
}
</script>
