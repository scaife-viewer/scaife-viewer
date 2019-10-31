/* global describe, expect, it  */
import { shallowMount } from '@vue/test-utils';

import SearchResults from '../static/src/js/library/search/SearchResults.vue';
import searchResultsJson from './fixtures/search-results.json';


describe('SearchResults.vue', () => {
  it('displays the search results correctly if no results are found', () => {
    const wrapper = shallowMount(SearchResults, {
      propsData: {
        secondLoading: false,
        results: [],
        createPassageLink: () => true,
        searchResultsType: 'instances',
      },
    });
    expect(wrapper.text()).toBeFalsy();
  });

  it('displays the search results correctly if results are found', () => {
    const wrapper = shallowMount(SearchResults, {
      propsData: {
        secondLoading: false,
        results: searchResultsJson,
        createPassageLink: () => true,
        searchResultsType: 'instances',
      },
    });
    expect(wrapper.text()).toContain('The Six Books of a Commonweale');
  });

  it('displays the search results correctly when results type is "instances"', () => {
    const wrapper = shallowMount(SearchResults, {
      propsData: {
        secondLoading: false,
        results: searchResultsJson,
        createPassageLink: () => true,
        searchResultsType: 'instances',
      },
    });
    expect(wrapper.text()).toContain('The Six Books of a Commonweale');
    expect(wrapper.html()).toContain('<span> Lords , That <em>Bodin</em> at his pleasure had over ruled the Estates</span>');
  });

  it('displays the search results correctly when results type is "passages"', () => {
    const wrapper = shallowMount(SearchResults, {
      propsData: {
        secondLoading: false,
        results: searchResultsJson,
        createPassageLink: () => true,
        searchResultsType: 'passages',
      },
    });
    expect(wrapper.text()).toContain('The Six Books of a Commonweale');
    expect(wrapper.html()).not.toContain('<span> Lords , That <em>Bodin</em> at his pleasure had over ruled the Estates</span>');
  });
});
