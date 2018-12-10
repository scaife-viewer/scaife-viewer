import {
  CTSTocList,
  CTSWorkList,
  Library
} from '../library';
import { Reader } from '../reader';

export default [
  { path: '/library', component: Library, name: 'library' },
  { path: '/library/toc/:urn', component: CTSTocList, name: 'library_text' },
  { path: '/library/:urn', component: CTSWorkList, name: 'library_textgroup' },
  { path: '/reader/urn::leftUrn', component: Reader, name: 'reader' },
];
