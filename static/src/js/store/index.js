const Vue = require('vue');
const Vuex = require('vuex');
const createPersistedState = require('vuex-persistedstate');
const library = require('./library');

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    library,
  },
  plugins: [
    createPersistedState({
      paths: ['a'],
      storage: window.localStorage,
    }),
  ],
});

export default store;
