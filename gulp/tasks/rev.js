/**
 * Dependencies
 */
const gulp = require('gulp');
const rev  = require('gulp-rev');

/**
 * Module body / Expose
 */
module.exports = (entry, config) => {
  config = config || {};
  return gulp.src(entry)
    .pipe(rev());
};
