<template>
  <div class="reader-loader" :style="containerStyle">
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
    <div :style="[ spinnerStyle() ]"></div>
  </div>
</template>

<script>
export default {
  name: 'ReaderLoader',
  props: {
    color: {
      type: String,
      default: '#343a40',
    },
    size: {
      type: String,
      default: '15px',
    },
    margin: {
      type: String,
      default: '2px',
    },
    radius: {
      type: String,
      default: '100%',
    },
  },
  computed: {
    containerStyle() {
      return {
        width: `${(parseFloat(this.size) * 3) + (parseFloat(this.margin) * 6)}px`,
        fontSize: 0,
      };
    },
  },
  methods: {
    random(value) {
      return Math.random() * value;
    },
    delay() {
      return `${((this.random(100) / 100) - 0.2)}s`;
    },
    duration() {
      return `${((this.random(100) / 100) + 0.6)}s`;
    },
    spinnerStyle() {
      return {
        backgroundColor: this.color,
        width: this.size,
        height: this.size,
        margin: this.margin,
        borderRadius: this.radius,
        animationName: 'v-grid-stretch-delay',
        animationIterationCount: 'infinite',
        animationTimingFunction: 'ease',
        animationFillMode: 'both',
        display: 'inline-block',
        animationDelay: this.delay(),
        animationDuration: this.duration(),
      };
    },
  },
};
</script>

<style lang="scss">
.reader-loader {
  margin: auto;
  transform: translate3d(0, 0, 0);  // to avoid flicker
  @keyframes v-grid-stretch-delay {
      0% {
        transform: scale(1);
      }
      50% {
        transform: scale(0.5);
        opacity: 0.7;
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
  }
}
</style>
