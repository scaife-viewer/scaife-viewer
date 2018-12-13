<template>
    <font-awesome-icon :icon="icon" v-if="inline"></font-awesome-icon>
    <font-awesome-icon :icon="icon" v-else fixed-width></font-awesome-icon>
</template>
<script>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import iconMap from './icons';

export default {
    name: 'icon',
    props: ['name', 'inline'],
    components: {
        FontAwesomeIcon
    },
    computed: {
        icon() {
            return iconMap[this.name];
        }
    }
}
</script>
