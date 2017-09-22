/**
 * Dependencies
 */
const path    = require('path');
const modules = {};

/**
 * Module body
 */
const load = function load(name) {
  return require(path.resolve(__dirname, name));
};

const tasks = [
  'clean',
  'css',
  'browserify',
  'test',
  'xo',
  'rev',
  'manifest',
  'cleanup',
  'copy',
  'handlebars',
  'optimizejs',
  'optimizecss'
];

tasks.forEach(task => {
  modules[task] = load(task);
});

/**
 * Expose
 */
exports = module.exports = modules;
