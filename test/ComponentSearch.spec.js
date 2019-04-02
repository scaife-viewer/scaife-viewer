/* global describe, expect, it  */
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';

import Search from '../static/src/js/library/search/Search.vue';
import createStore from '../static/src/js/config';
import searchResultsJson from './fixtures/search-results.json';

const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(Vuex);
localVue.use(VueRouter);


describe('Search.vue', () => {
  const config = createStore();
  const store = new Vuex.Store(config);

  it('sets the correct default data', () => {
    const wrapper = shallowMount(Search, {
      store,
      localVue,
      stubs: { BaseWidget: true },
      router,
    });

    expect(wrapper.text()).toContain('Search Guide');
    expect(wrapper.text()).toContain('Form');
    expect(wrapper.text()).toContain('Lemma (Greek only)');
  });

  it('displays the search results correctly if no results are found', () => {
    const wrapper = shallowMount(Search, {
      store,
      localVue,
      stubs: { BaseWidget: true },
      router,
    });
    wrapper.setData({
      showSearchResults: true,
      totalPages: 0,
      pageNum: 1,
      startIndex: 1,
      endIndex: 10,
      hasNext: false,
      hasPrev: false,
      totalResults: 0,
      results: [],
      textGroups: [],
      secondLoading: false,
      loading: false,
    });
    expect(wrapper.text()).toContain('No results found. Please try again.');
  });

  it('displays the search results correctly if results are found', () => {
    const wrapper = shallowMount(Search, {
      store,
      localVue,
      stubs: { BaseWidget: true },
      router,
    });
    wrapper.setData({
      showSearchResults: true,
      totalPages: 1,
      pageNum: 1,
      startIndex: 1,
      endIndex: 10,
      hasNext: false,
      hasPrev: false,
      totalResults: 4,
      results: searchResultsJson,
      textGroups: [],
      secondLoading: false,
      loading: false,
    });
    expect(wrapper.text()).toContain('The Six Books of a Commonweale');
  });
});
