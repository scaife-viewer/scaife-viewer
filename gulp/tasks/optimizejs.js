const gulp   = require('gulp');
const uglify = require('gulp-uglify');
const size   = require('gulp-size');


module.exports = (source, options, dist) => {
    return gulp.src(source)
        .pipe(uglify(options))
        .pipe(gulp.dest(dist))
        .pipe(size());
};
