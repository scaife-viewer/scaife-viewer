/* global describe, expect, it  */
import { shallowMount } from '@vue/test-utils';

import SearchResults from '../static/src/js/library/search/SearchResults.vue';
import searchResultsJson from './fixtures/search-results.json';


describe('Search.vue', () => {
  it('displays the search results correctly if no results are found', () => {
    const wrapper = shallowMount(SearchResults, {
      propsData: {
        results: [],
        secondLoading: false,
        createPassageLink: () => true,
      },
    });
    expect(wrapper.text()).toContain('');
  });

  it('displays the search results correctly if results are found', () => {
    const wrapper = shallowMount(SearchResults, {
      propsData: {
        results: searchResultsJson,
        secondLoading: false,
        createPassageLink: () => true,
      },
    });
    expect(wrapper.text()).toContain('The Six Books of a Commonweale');
  });
});
