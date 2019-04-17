import Vue from 'vue';
import Vuex from 'vuex';

import createStore from './config';

Vue.use(Vuex);

export default new Vuex.Store(createStore());
