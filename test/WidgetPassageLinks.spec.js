/* global describe, expect, it  */
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';

import WidgetPassageLinks from '../static/src/js/reader/widgets/WidgetPassageLinks.vue';

const localVue = createLocalVue();
localVue.use(Vuex);


const store = new Vuex.Store({
  state: {
    reader: { rightPassage: 0 },
  },
  getters: {
    'reader/passage': () => {
      const obj = { urn: 'urn:cts:latinLit:phi1002.phi001.perseus-eng2:pr.pr.1-pr.pr.3' };
      return obj;
    },
  },
});

const mocks = {
  $store: store,
  $router: {
    options: { base: '/' },
  },
};

describe('WidgetPassageLinks.vue', () => {
  it('displays the URN properly when there is no CTS_API_ENDPOINT', () => {
    const wrapper = shallowMount(WidgetPassageLinks, {
      mocks,
      stubs: { BaseWidget: true },
    });
    expect(wrapper.text()).toBe('CTS URN urn:cts:latinLit:phi1002.phi001.perseus-eng2:pr.pr.1-pr.pr.3');
  });
});
