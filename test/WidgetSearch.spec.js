/* global describe, expect, it  */
import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';

import WidgetSearch from '../static/src/js/reader/widgets/WidgetSearch.vue';
import createStore from '../static/src/js/config';

const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(Vuex);
localVue.use(VueRouter);


describe('WidgetSearch.vue', () => {

  const config = createStore();
  const store = new Vuex.Store(config);

  it('sets the correct default data', () => {
    const wrapper = shallowMount(WidgetSearch, {
      store,
      localVue,
      stubs: { BaseWidget: true },
      router,
    });

    expect(wrapper.text()).toContain('Text Search');
    expect(wrapper.text()).toContain('Form Lemma (Greek only)');
    expect(wrapper.text()).toContain('Use text input above to find text in this version.');

    const input = wrapper.find('input[type="text"]');
    input.element.value = 'input';
    input.trigger('input');
    expect(wrapper.text()).not.toContain('Use text input above to find text in this version.');
  });

  it('displays the search results correctly', () => {
    const wrapper = shallowMount(WidgetSearch, {
      store,
      localVue,
      stubs: { BaseWidget: true },
      router,
    });
    wrapper.setData({
      results: [
        {
          passage:
            {
              url: '/reader/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.7/',
              json_url: '/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.7/json/',
              text: {
                url: '/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/',
                json_url: '/library/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/json/',
                text_url: '/library/passage/urn:cts:pdlpsci:bodin.livrep.perseus-eng1/text/',
                ancestors: [
                  {
                    url: '/library/urn:cts:pdlpsci:bodin/',
                    json_url: '/library/urn:cts:pdlpsci:bodin/json/',
                    text_url: '/library/passage/urn:cts:pdlpsci:bodin/text/',
                    urn: 'urn:cts:pdlpsci:bodin',
                    label: 'Bodin',
                  },
                  {
                    url: '/library/urn:cts:pdlpsci:bodin.livrep/',
                    json_url: '/library/urn:cts:pdlpsci:bodin.livrep/json/',
                    text_url: '/library/passage/urn:cts:pdlpsci:bodin.livrep/text/',
                    urn: 'urn:cts:pdlpsci:bodin.livrep',
                    label: 'The Six Books of a Commonweale',
                  },
                ],
                urn: 'urn:cts:pdlpsci:bodin.livrep.perseus-eng1',
                label: '1606 The Six Books of a Commonweale',
                lang: 'eng',
                human_lang: 'English',
                kind: 'translation',
              },
              urn: 'urn:cts:pdlpsci:bodin.livrep.perseus-eng1:3.7',
              refs: {
                start: {
                  reference: '3.7',
                  human_reference: 'Book 3 Chapter 7',
                }
              },
              ancestors: [
                { reference: '3' },
              ],
              children: [],
            },
        },
      ],
      totalCount: 1,
    });
    expect(wrapper.html()).toContain('Book 3 Chapter 7');
  });
});
