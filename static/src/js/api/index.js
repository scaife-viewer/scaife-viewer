import HTTP from './http';
import pagination from './pagination';

const chunkFunc = require('lodash.chunk');
const mergeFunc = require('lodash.merge');


async function chunkedVectorRequest(urn, params) {
  const urns = params.e;
  delete params.e;
  const chunks = chunkFunc(urns, 100);
  const requests = [];
  chunks.forEach((chunk) => {
    params = { e: chunk };
    // vector for texts
    requests.push(HTTP.get(`library/vector/${urn}/`, { params }));
  });
  const responses = await Promise.all(requests);
  const allData = {};
  responses.flatMap(response => response.data).flatMap(data => data).forEach((obj) => {
    mergeFunc(allData, obj);
  });
  return allData;
}

export default {
  getTextGroupList: cb => HTTP.get('library/json/').then(r => cb(r.data)),
  getLibraryVector: (urn, params, cb) => chunkedVectorRequest(urn, params).then(data => cb(data)),
  getCollection: (urn, cb) => HTTP.get(`library/${urn}/json/`)
    .then(r => cb(r.data))
    .catch((err) => {
      if (err.response && err.response.data && err.response.data.error) {
        const { error } = err.response.data;
        if (error.includes('refsDecl')) {
          throw new Error('There is a problem with the XML for this document that prevents it from being shown.');
        } else {
          throw new Error(err.response.data.error);
        }
      } else {
        throw new Error(err);
      }
    }),
  getPassage: (urn, cb) => HTTP.get(`library/passage/${urn}/json/`)
    .then(r => cb({ ...r.data, ...pagination(r) })),
  searchText: (params, url, cb) => HTTP.get('search/json/', { params }).then(r => cb(r.data)),
  getLibraryInfo: cb => HTTP.get('library/json/info').then(r => cb(r.data)),
};
