/* global describe, expect, it  */
import { shallowMount } from '@vue/test-utils';

import SearchWorks from '../static/src/js/library/search/SearchWorks.vue';
import worksLargeJson from './fixtures/works-large.json';
import worksSmallJson from './fixtures/works-small.json';


describe('SearchWorks.vue', () => {
  it('displays the works correctly when there are more than ten works', () => {
    const wrapper = shallowMount(SearchWorks, {
      propsData: {
        handleSearch: () => true,
        works: worksLargeJson,
        showClearWork: false,
        showWorks: false,
        handleShowWorksChange: () => true,
        textGroup: () => false,
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

  it('displays the works correctly when there are less than ten works', () => {
    const wrapper = shallowMount(SearchWorks, {
      propsData: {
        handleSearch: () => true,
        works: worksSmallJson,
        showClearWork: false,
        showWorks: false,
        handleShowWorksChange: () => true,
        textGroup: () => false,
      },
    });
    expect(wrapper.text()).not.toContain('See More');
  });

  it('displays the works correctly when one work is selected', () => {
    const wrapper = shallowMount(SearchWorks, {
      propsData: {
        handleSearch: () => true,
        works: [
          {
            text_group: {
              urn: 'urn:cts:greekLit:tlg0059.tlg011',
              label: 'Symposium',
              texts: [
                {
                  urn: 'urn:cts:greekLit:tlg0059.tlg011.perseus-grc2',
                },
                {
                  urn: 'urn:cts:greekLit:tlg0059.tlg011.perseus-eng2',
                },
              ],
            },
            count: 38,
          },
        ],
        showClearWork: true,
        showWorks: false,
        handleShowWorksChange: () => true,
        textGroup: () => false,
      },
    });
    expect(wrapper.text()).toContain('clear');
    expect(wrapper.text()).not.toContain('See More');
  });
});
