const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const webpack = require('webpack');
const utils = require('./utils');

const env = {};

module.exports = merge(common, {
  devtool: '#source-map',
  module: {
    rules: utils.styleLoaders(),
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': env,
    }),
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false,
      },
      sourceMap: true,
    }),
  ],
});
