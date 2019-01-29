/* global $ */
import Vue from 'vue';

// @@@ not used
// Vue.directive('tooltip', (el, binding) => {
//   $(el).tooltip({
//     title: binding.value,
//     placement: binding.arg,
//     trigger: 'hover',
//   });
// });

Vue.directive('popover', (el, binding) => {
  $(el).popover({
    placement: binding.arg,
    ...binding.value,
  });
});
