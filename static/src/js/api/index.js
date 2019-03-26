import HTTP from './http';
import pagination from './pagination';

export default {
  getTextGroupList: cb => HTTP.get('library/json/').then(r => cb(r.data)),
  getLibraryVector: (urn, params, cb) => HTTP.get(`library/vector/${urn}/`, { params }).then(r => cb(r.data)),
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
  searchText: (params, url, cb) => HTTP.get(url, { params }).then(r => cb(r.data)),
};
