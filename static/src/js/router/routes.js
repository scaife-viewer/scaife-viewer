export default [
  {
    path: '/library',
    component: import(/* webpackChunkName: "library" */ '../library/Library.vue'),
    name: 'library',
  },
  {
    path: '/library/:urn',
    component: import(/* webpackChunkName: "library_urn" */ '../library/CTSView.vue'),
    name: 'library_urn',
  },
  {
    path: '/reader/:leftUrn',
    component: import(/* webpackChunkName: "reader" */ '../reader/Reader.vue'),
    name: 'reader',
  },
  {
    path: '/search',
    component: import(/* webpackChunkName: "search" */ '../library/search/Search.vue'),
    name: 'search',
  },
];
