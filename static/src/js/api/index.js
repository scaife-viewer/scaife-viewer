import HTTP from './http';
import qs from 'query-string';

export default {
  getTextGroupList: cb => HTTP.get('library/json/').then(r => cb(r.data)),
  getLibraryVector: (urn, params, cb) => HTTP.get(`library/vector/${urn}/?${qs.stringify({ e: params })}`).then(r => cb(r.data)),
  getCollection: (urn, cb) => HTTP.get(`library/${urn}/json/`).then(r => cb(r.data)),
  getPassage: (urn, cb) => HTTP.get(`library/passage/${urn}/json/`).then(r => cb(r.data)),
  searchText: (params, cb) => HTTP.get('search/json/', { params }).then(r => cb(r.data)),
};
