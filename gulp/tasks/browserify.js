/**
 * Dependencies
 */
const path = require('path');
const browserify = require('browserify');
const babelify   = require('babelify');
const source     = require('vinyl-source-stream');

/**
 * Module body / Expose
 */
module.exports = (entry, config) => {
  config = config || {};
  const built = browserify(entry)
    .transform(babelify);
  return built.bundle().pipe(source(path.basename(entry)));
};
