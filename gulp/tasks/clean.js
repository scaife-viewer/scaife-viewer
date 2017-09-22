/**
 * Dependencies
 */
const del = require('del');

/**
 * Module body / Expose
 */
module.exports = (entry, config) => {
  config = config || {};
  return del(entry, config);
};
