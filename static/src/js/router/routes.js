import {
  CTSView,
  Library,
  Search,
} from '../library';
import Reader from '../reader';

export default [
  { path: '/library', component: Library, name: 'library' },
  { path: '/library/:urn', component: CTSView, name: 'library_urn' },
  { path: '/reader/:leftUrn', component: Reader, name: 'reader' },
  { path: '/search', component: Search, name: 'search' },
];
