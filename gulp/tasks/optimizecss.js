const gulp = require('gulp');
const nano = require('gulp-cssnano');
const size = require('gulp-size');


module.exports = (source, options, dist) => {
    return gulp.src(source)
        .pipe(nano(options))
        .pipe(gulp.dest(dist))
        .pipe(size());
};
