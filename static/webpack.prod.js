const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const utils = require('./utils');

const env = {
  NODE_ENV: '"production"',
};
const extractCss = new ExtractTextPlugin('css/app.css');

module.exports = merge(common, {
  devtool: '#source-map',
  module: {
    rules: utils.styleLoaders({ extracter: extractCss }),
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
    extractCss,
  ],
});
