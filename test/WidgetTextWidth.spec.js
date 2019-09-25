/* global describe, expect, it  */
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';

import WidgetTextWidth from '../static/src/js/reader/widgets/WidgetTextWidth.vue';
import createStore from '../static/src/js/config';

const localVue = createLocalVue();
localVue.use(Vuex);

describe('WidgetTextWidth.vue', () => {
  const store = new Vuex.Store(createStore());

  it('sets the correct default data', () => {
    const wrapper = shallowMount(WidgetTextWidth, {
      store,
      localVue,
      stubs: { BaseWidget: true },
    });
    const normalSpan = wrapper.findAll('span').at(2);

    expect(wrapper.text()).toBe('Text Width Narrow Normal Wide Full');
    expect(normalSpan.html()).toBe('<span class="text-width-control active">Normal</span>');
    expect(store.state.reader.textWidth).toBe('normal');
  });

  it('updates the "textWidth" appropriately', () => {
    const wrapper = shallowMount(WidgetTextWidth, {
      store,
      localVue,
      stubs: { BaseWidget: true },
    });
    const narrowSpan = wrapper.findAll('span').at(1);
    const normalSpan = wrapper.findAll('span').at(2);
    const wideSpan = wrapper.findAll('span').at(3);

    expect(narrowSpan.html()).toBe('<span class="text-width-control">Narrow</span>');
    expect(normalSpan.html()).toBe('<span class="text-width-control active">Normal</span>');
    expect(wideSpan.html()).toBe('<span class="text-width-control">Wide</span>');
    expect(store.state.reader.textWidth).toBe('normal');

    wideSpan.trigger('click');
    expect(narrowSpan.html()).toBe('<span class="text-width-control">Narrow</span>');
    expect(normalSpan.html()).toBe('<span class="text-width-control">Normal</span>');
    expect(wideSpan.html()).toBe('<span class="text-width-control active">Wide</span>');
    expect(store.state.reader.textWidth).toBe('wide');

    narrowSpan.trigger('click');
    expect(narrowSpan.html()).toBe('<span class="text-width-control active">Narrow</span>');
    expect(normalSpan.html()).toBe('<span class="text-width-control">Normal</span>');
    expect(wideSpan.html()).toBe('<span class="text-width-control">Wide</span>');
    expect(store.state.reader.textWidth).toBe('narrow');

    normalSpan.trigger('click');
    expect(narrowSpan.html()).toBe('<span class="text-width-control">Narrow</span>');
    expect(normalSpan.html()).toBe('<span class="text-width-control active">Normal</span>');
    expect(wideSpan.html()).toBe('<span class="text-width-control">Wide</span>');
    expect(store.state.reader.textWidth).toBe('normal');
  });
});
