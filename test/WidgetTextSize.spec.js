/* global describe, expect, it  */
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';

import WidgetTextSize from '../static/src/js/reader/widgets/WidgetTextSize.vue';
import WidgetTextWidth from '../static/src/js/reader/widgets/WidgetTextWidth.vue';
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
    // default text width should be "normal"
    expect(store.state.reader.textWidth).toBe('normal');

    largeSpan.trigger('click');
    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg active">Αα</span>');
    expect(store.state.reader.textSize).toBe('lg');
    // default text width should be "normal"
    expect(store.state.reader.textWidth).toBe('normal');

    smallSpan.trigger('click');
    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm active">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg">Αα</span>');
    expect(store.state.reader.textSize).toBe('sm');
    // default text width should be "normal"
    expect(store.state.reader.textWidth).toBe('normal');

    mediumSpan.trigger('click');
    expect(smallSpan.html()).toBe('<span class="text-size-control text-sm">Αα</span>');
    expect(mediumSpan.html()).toBe('<span class="text-size-control text-md active">Αα</span>');
    expect(largeSpan.html()).toBe('<span class="text-size-control text-lg">Αα</span>');
    expect(store.state.reader.textSize).toBe('md');
    // default text width should be "normal"
    expect(store.state.reader.textWidth).toBe('normal');
  });

  it('when the "textSize" is changed "textWidth" is changed to "normal"', () => {
    const textSizeWrapper = shallowMount(WidgetTextSize, {
      store,
      localVue,
      stubs: { BaseWidget: true },
    });
    const textWidthWrapper = shallowMount(WidgetTextWidth, {
      store,
      localVue,
      stubs: { BaseWidget: true },
    });

    const smallSpan = textSizeWrapper.findAll('span').at(2);
    const largeSpan = textSizeWrapper.findAll('span').at(4);

    const narrowSpan = textWidthWrapper.findAll('span').at(1);
    const wideSpan = textWidthWrapper.findAll('span').at(3);

    expect(store.state.reader.textWidth).toBe('normal');

    wideSpan.trigger('click');
    expect(store.state.reader.textWidth).toBe('wide');
    largeSpan.trigger('click');
    expect(store.state.reader.textWidth).toBe('normal');

    narrowSpan.trigger('click');
    expect(store.state.reader.textWidth).toBe('narrow');
    smallSpan.trigger('click');
    expect(store.state.reader.textWidth).toBe('normal');
  });
});
