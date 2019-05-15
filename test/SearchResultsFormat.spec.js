/* global describe, expect, it  */
import { shallowMount } from '@vue/test-utils';

import SearchResultsFormat from '../static/src/js/library/search/SearchResultsFormat.vue';


describe('SearchResultsFormat.vue', () => {
  it('displays correctly', () => {
    const wrapper = shallowMount(SearchResultsFormat, {
      propsData: {
        searchResultsType: 'instances',
        handleResultsTypeChange: () => true,
      },
    });
    expect(wrapper.text()).toContain('Results Format  Instances  Passages');
  });
});
