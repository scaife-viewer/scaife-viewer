import qs from 'query-string';

import HTTP from './http';
import pagination from './pagination';

export default {
  getTextGroupList: cb => HTTP.get('library/json/').then(r => cb(r.data)),
  getLibraryVector: (urn, params, cb) => HTTP.get(`library/vector/${urn}/?${qs.stringify({ e: params })}`).then(r => cb(r.data)),
  getCollection: (urn, cb) => HTTP.get(`library/${urn}/json/`).then(r => cb(r.data)),
  getPassage: (urn, cb) => HTTP.get(`library/passage/${urn}/json/`)
    .then(r => cb({ ...r.data, ...pagination(r) })),
  searchText: (params, url, cb) => HTTP.get(url, { params }).then(r => cb(r.data)),
};
