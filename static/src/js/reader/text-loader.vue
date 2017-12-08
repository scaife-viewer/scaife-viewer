<template>
  <div v-show="show" :style="{ 'text-align': 'center' }">
    <div :style="[ spinnerStyle, spinnerDelay1 ]"></div>
    <div :style="[ spinnerStyle, spinnerDelay2 ]"></div>
    <div :style="[ spinnerStyle, spinnerDelay3 ]"></div>
  </div>
</template>

<script>
export default {
  mounted() {
    setTimeout(() => {
      this.show = true;
    }, 200);
  },
  props: {
    color: {
      type: String,
      default: '#ccc',
    },
    size: {
      type: String,
      default: '10px',
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
  data() {
    return {
      show: false,
      spinnerStyle: {
        backgroundColor: this.color,
        width: this.size,
        height: this.size,
        margin: this.margin,
        borderRadius: this.radius,
        display: 'inline-block',
        animationName: 'v-pulse-stretch-delay',
        animationDuration: '0.75s',
        animationIterationCount: 'infinite',
        animationTimingFunction: 'cubic-bezier(.2, .68, .18, 1.08)',
        animationFillMode: 'both',
      },
      spinnerDelay1: {
        animationDelay: '0.12s',
      },
      spinnerDelay2: {
        animationDelay: '0.24s',
      },
      spinnerDelay3: {
        animationDelay: '0.36s',
      },
    };
  },
};
</script>

<style lang="scss">
@keyframes v-pulse-stretch-delay {
  0%, 80% {
    transform: scale(1);
    opacity: 1;
  }
  45% {
    transform: scale(0.1);
    opacity: 0.7;
  }
}
</style>
