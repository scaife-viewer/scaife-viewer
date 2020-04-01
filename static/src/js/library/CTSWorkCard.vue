<template>
  <div class="version-card">
    <div class="card-body">
      <p class="text-subtype">
        {{ text.kind }}
      </p>
      <h4 class="card-title">
        <a :href="libraryURL">{{ text.label }}</a>
      </h4>
      <p class="card-text">
        {{ text.description }}
      </p>
    </div>
    <div class="card-footer">
      <a :href="readerURL"><icon name="book" /> Read ({{ text.humanLang }})</a>
    </div>
  </div>
</template>

<script>
  import { safeURN } from '../urn';

  export default {
    props: ['text'],
    computed: {
      libraryURL() {
        return `/library/${safeURN(this.text.urn)}/`;
      },
      readerURL() {
        return `/library/${safeURN(this.text.urn)}/redirect/`;
      }
    }
  }
</script>
