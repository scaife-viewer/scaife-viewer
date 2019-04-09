<template>
    <cts-work-list v-if="isWorkList"></cts-work-list>
    <cts-version-list v-else-if="isVersionList"></cts-version-list>
    <cts-toc-list v-else></cts-toc-list>
</template>
<script>
import URN from '../urn';

import CTSTocList from './CTSTocList.vue';
import CTSVersionList from './CTSVersionList.vue';
import CTSWorkList from './CTSWorkList.vue';

export default {
    name: 'cts-view',
    components: {
        'cts-toc-list': CTSTocList,
        'cts-version-list': CTSVersionList,
        'cts-work-list': CTSWorkList
    },
    computed: {
        isWorkList() {
            const urn = new URN(this.$route.params.urn);
            return urn.work === null;
        },
        isVersionList() {
            const urn = new URN(this.$route.params.urn);
            return urn.version === null;
        }
    }
}
</script>
