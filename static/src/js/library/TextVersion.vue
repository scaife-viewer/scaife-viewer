<template>
    <a class="badge badge-light"
      :href="getReaderURL(text)"
      v-popover:bottom="{title: text.label, content: text.description, trigger: 'hover'}"
    >
        {{ text.lang }}
    </a>
</template>

<script>
export default {
    props: ['text'],
    methods: {
        getReaderURL(version) {
        // @@@ prefer firstPassageUrl
        return `/library/${this.safeURN(version.urn)}/redirect/`;
        },
        safeURN(urn) {
        // @@@ maintain backwards compatability
        return urn.endsWith(':') ? urn.slice(0, -1) : urn;
        },
    }
}
</script>
