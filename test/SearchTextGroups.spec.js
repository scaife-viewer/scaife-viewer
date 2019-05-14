/* global describe, expect, it  */
import { shallowMount } from '@vue/test-utils';

import SearchTextGroups from '../static/src/js/library/search/SearchTextGroups.vue';
import textGroupsLargeJson from './fixtures/text-groups-large.json';
import textGroupsSmallJson from './fixtures/text-groups-small.json';


describe('SearchTextGroups.vue', () => {
  it('displays the text groups correctly when there are more than ten text groups', () => {
    const wrapper = shallowMount(SearchTextGroups, {
      propsData: {
        handleSearch: () => true,
        textGroups: textGroupsLargeJson,
        showClearTextGroup: false,
        showTextGroups: false,
        handleShowTextGroupsChange: () => true,
        clearWorkGroups: () => false,
      },
    });
    expect(wrapper.text()).toContain('See More');
    const button = wrapper.find('span.link-text');
    button.trigger('click');
    expect(wrapper.text()).not.toContain('See More');
    expect(wrapper.text()).toContain('See Less');
    button.trigger('click');
    expect(wrapper.text()).not.toContain('See Less');
    expect(wrapper.text()).toContain('See More');
  });

  it('displays the text groups correctly when there are less than ten text groups', () => {
    const wrapper = shallowMount(SearchTextGroups, {
      propsData: {
        handleSearch: () => true,
        textGroups: textGroupsSmallJson,
        showClearTextGroup: false,
        showTextGroups: false,
        handleShowTextGroupsChange: () => true,
        clearWorkGroups: () => false,
      },
    });
    expect(wrapper.text()).not.toContain('See More');
  });

  it('displays the text groups correctly when one is selected', () => {
    const wrapper = shallowMount(SearchTextGroups, {
      propsData: {
        handleSearch: () => true,
        textGroups: [
          {
            text_group: {
              urn: 'urn:cts:farsiLit:hafez',
              label: 'Hafez',
              works: [
                {
                  urn: 'urn:cts:farsiLit:hafez.divan',
                  texts: [
                    {
                      urn: 'urn:cts:farsiLit:hafez.divan.perseus-far1'
                    },
                    {
                      urn: 'urn:cts:farsiLit:hafez.divan.perseus-eng1'
                    },
                    {
                      urn: 'urn:cts:farsiLit:hafez.divan.perseus-ger1'
                    },
                  ],
                },
              ],
            },
            count: 507,
          },
        ],
        showClearTextGroup: true,
        showTextGroups: false,
        handleShowTextGroupsChange: () => true,
        clearWorkGroups: () => false,
      },
    });
    expect(wrapper.text()).toContain('clear');
    expect(wrapper.text()).not.toContain('See More');
  });
});
