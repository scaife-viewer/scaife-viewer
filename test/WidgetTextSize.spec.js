/* global describe, expect, it  */
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';

import WidgetTextSize from '../static/src/js/reader/widgets/WidgetTextSize.vue';
import createStore from '../static/src/js/config';

const localVue = createLocalVue();
localVue.use(Vuex);

describe('WidgetTextSize.vue', () => {
  const store = new Vuex.Store(createStore());

  it('sets the correct default data', () => {
    const wrapper = shallowMount(WidgetTextSize, {
      store,
      localVue,
      stubs: { BaseWidget: true },
    });
    const mediumSpan = wrapper.findAll('span').at(3);

    expect(wrapper.text()).toBe('Text Size Αα Αα Αα Αα Αα');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md active">Αα</span>');
    expect(store.state.reader.textSize).toBe('md');
  });

  it('updates the "textSize" appropriately', () => {
    const wrapper = shallowMount(WidgetTextSize, {
      store,
      localVue,
      stubs: { BaseWidget: true },
    });
    const smallSpan = wrapper.findAll('span').at(2);
    const mediumSpan = wrapper.findAll('span').at(3);
    const largeSpan = wrapper.findAll('span').at(4);

    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md active">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg">Αα</span>');
    expect(store.state.reader.textSize).toBe('md');

    largeSpan.trigger('click');
    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg active">Αα</span>');
    expect(store.state.reader.textSize).toBe('lg');

    smallSpan.trigger('click');
    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm active">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg">Αα</span>');
    expect(store.state.reader.textSize).toBe('sm');

    mediumSpan.trigger('click');
    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md active">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg">Αα</span>');
    expect(store.state.reader.textSize).toBe('md');
  });
});
