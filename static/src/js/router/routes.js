import {
  CTSView,
  Library,
} from '../library';
import Reader from '../reader';

export default [
  { path: '/library', component: Library, name: 'library' },
  { path: '/library/:urn', component: CTSView, name: 'library_urn' },
  { path: '/reader/urn::leftUrn', component: Reader, name: 'reader' },
];
