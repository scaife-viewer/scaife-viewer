import qs from 'query-string';

import HTTP from './http';

export default {
  getTextGroupList: cb => HTTP.get('library/json/').then(r => cb(r.data)),
  getWorkList: (textGroupUrl, cb) => HTTP.get(textGroupUrl).then(r => cb(r.data)),  // really just need urn and then call getCollection
  getLibraryVector: (urn, params, cb) => HTTP.get(`library/vector/${urn}/?${params}`).then(r => cb.data)),
  getTOCList: (textUrl, cb) => HTTP.get(textUrl).then(r => cb(r.data)), // really just need urn and then call getCollectionx

  getCollection: (urn, cb) => HTTP.get(`library/${urn}/json/`).then(r => cb(r.data)),
  getPassage: (urn, cb) => HTTP.get(`library/passage/${urn}/json/`).then(r => cb(r.data)),
  searchText: (params, cb) => HTTP.get(`search/json/?${qs.stringify(params)}`).then(r => cb(r.data)),
};
