/**
 * Dependencies
 */
const rev = require('gulp-rev');

/**
 * Module body / Expose
 */
module.exports = config => {
  config = config || {};
  config.path = config.path || 'manifest.json';
  return rev.manifest(config);
};
