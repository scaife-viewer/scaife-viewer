/**
 * Dependencies
 */
const cleanup = require('gulp-cleanup');

/**
 * Module body / Expose
 */
module.exports = config => {
  config = config || {};
  return cleanup();
};
