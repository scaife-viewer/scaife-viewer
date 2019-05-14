/* global describe, expect, it  */
import { shallowMount } from '@vue/test-utils';

import SearchWorkGroups from '../static/src/js/library/search/SearchWorkGroups.vue';
import workGroupsLargeJson from './fixtures/work-groups-large.json';
import workGroupsSmallJson from './fixtures/work-groups-small.json';


describe('SearchWorkGroups.vue', () => {
  it('displays the work groups correctly when there are more than ten work groups', () => {
    const wrapper = shallowMount(SearchWorkGroups, {
      propsData: {
        handleSearch: () => true,
        workGroups: workGroupsLargeJson,
        showClearWorkGroup: false,
        showWorkGroups: false,
        handleShowWorkGroupsChange: () => true,
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

  it('displays the work groups correctly when there are less than ten work groups', () => {
    const wrapper = shallowMount(SearchWorkGroups, {
      propsData: {
        handleSearch: () => true,
        workGroups: workGroupsSmallJson,
        showClearWorkGroup: false,
        showWorkGroups: false,
        handleShowWorkGroupsChange: () => true,
        textGroup: () => false,
      },
    });
    expect(wrapper.text()).not.toContain('See More');
  });

  it('displays the work groups correctly when one is selected', () => {
    const wrapper = shallowMount(SearchWorkGroups, {
      propsData: {
        handleSearch: () => true,
        workGroups: [
          {
            text_group: {
              urn: 'urn:cts:greekLit:tlg0059.tlg011',
              label: 'Symposium',
              texts: [
                {
                  urn: 'urn:cts:greekLit:tlg0059.tlg011.perseus-grc2'
                },
                {
                  urn: 'urn:cts:greekLit:tlg0059.tlg011.perseus-eng2'
                },
              ],
            },
            count: 38,
          },
        ],
        showClearWorkGroup: true,
        showWorkGroups: false,
        handleShowWorkGroupsChange: () => true,
        textGroup: () => false,
      },
    });
    expect(wrapper.text()).toContain('clear');
    expect(wrapper.text()).not.toContain('See More');
  });
});
