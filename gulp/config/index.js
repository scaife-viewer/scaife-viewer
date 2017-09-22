const templatePath = 'scaife_viewer/templates/';
const staticRoot = 'static/';
const staticSource = staticRoot + 'src/';
const staticBuild = staticRoot + '_build/';
const staticDist = staticRoot + 'dist/';
const npmRoot = 'node_modules/';


exports = module.exports = {
    staticUrlRoot: '/site_media/static',
    paths: {
        source: staticSource,
        build: staticBuild,
        dist: staticDist
    },
    watch: {
        styles: [
            staticSource + 'less/**/*.less'
        ],
        scripts: [
            staticSource + 'js/**/*.js'
        ]
    },
    templates: {
        destination: templatePath,
        manifestPath: staticBuild + 'manifest.json',
        scriptsTemplate: staticSource + 'hbs/_scripts.hbs',
        stylesTemplate: staticSource + 'hbs/_styles.hbs',
    },
    fonts: {
        sources: [
            npmRoot + 'font-awesome/fonts/**.*',
            npmRoot + 'bootstrap/fonts/**.*',
        ],
        dist: staticDist + 'fonts/'
    },
    styles: {
        source: staticSource + 'less/site.less',
        dist: staticBuild + 'css/',
        npmPaths: [
            npmRoot + 'bootstrap/less',
            npmRoot + 'font-awesome/less',
            npmRoot
        ]
    },
    scripts: {
        main: staticSource + 'js/site.js',
        source: [
            staticSource + 'js/**/*'
        ],
        dist: staticBuild + 'js/'
    },
    images: {
        sources: [
            staticSource + 'images/**.*'
        ],
        dist: staticDist + 'images/'
    },
    manifest: {
        source: [
            staticBuild + '**/*.css',
            staticBuild + '**/*.js'
        ]
    },
    test: {
        all: 'test/**/*.test.js',
        req: 'test/req/*.test.js',
        components: 'test/components/*.test.js'
      },
    xo: {
       source: [
         'tasks/**/*.js',
         staticSource + '**/*.js'
       ]
   },
   optimize: {
     css: {
       source: staticDist + 'css/*.css',
       options: {},
       dist: staticDist + 'css/'
     },
     js: {
       source: staticDist + 'js/*.js',
       options: {},
       dist: staticDist + 'js/'
     }
   }
};
