const path = require('path');
const webpack = require('webpack');
const autoprefixer = require('autoprefixer');

const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const { VueLoaderPlugin } = require('vue-loader');

const devMode = process.env.NODE_ENV !== 'production';
const hotReload = process.env.HOT_RELOAD === '1';

const vueRule = {
  test: /\.vue$/,
  use: 'vue-loader',
  exclude: /node_modules/,
};

const styleRule = {
  test: /\.(sa|sc|c)ss$/,
  use: [
    MiniCssExtractPlugin.loader,
    { loader: 'css-loader', options: { sourceMap: true } },
    { loader: 'postcss-loader', options: { plugins: () => [autoprefixer({ browsers: ['last 2 versions'] })] } },
    'sass-loader',
  ],
};

const jsRule = {
  test: /\.js$/,
  loader: 'babel-loader',
  include: path.resolve('./static/src/js'),
  exclude: /node_modules/,
};

const assetRule = {
  test: /.(jpg|png|woff(2)?|eot|ttf|svg)$/,
  loader: 'file-loader',
};

const plugins = [
  new webpack.ProvidePlugin({
    'window.jQuery': 'jquery',
    jQuery: 'jquery',
    $: 'jquery',
  }),
  new BundleTracker({ filename: './webpack-stats.json' }),
  new VueLoaderPlugin(),
  new MiniCssExtractPlugin({
    filename: devMode ? '[name].css' : '[name].[hash].css',
    chunkFilename: devMode ? '[id].css' : '[id].[hash].css',
  }),
  new BundleAnalyzerPlugin({ analyzerMode: 'static', openAnalyzer: false }),
  new webpack.HotModuleReplacementPlugin(),
  new CleanWebpackPlugin(['./static/dist']),
  new CopyWebpackPlugin([
    { from: './static/src/images/**/*', to: path.resolve('./static/dist/images/[name].[ext]'), toType: 'template' },
  ]),
  new webpack.EnvironmentPlugin([
    'NODE_ENV',
    'FORCE_SCRIPT_NAME',
  ]),
];

if (devMode) {
  styleRule.use = ['css-hot-loader', ...styleRule.use];
}

module.exports = {
  context: __dirname,
  entry: [
    '@babel/polyfill',
    './static/src/js/index.js',
  ],
  output: {
    path: path.resolve('./static/dist/'),
    filename: '[name]-[hash].js',
    publicPath: hotReload ? 'http://localhost:8080/' : '',
  },
  devtool: devMode ? 'cheap-eval-source-map' : 'source-map',
  devServer: {
    hot: true,
    quiet: false,
    headers: { 'Access-Control-Allow-Origin': '*' },
  },
  module: { rules: [vueRule, jsRule, styleRule, assetRule] },
  externals: { jquery: 'jQuery' },
  plugins,
  resolve: {
    alias: {
      '@': path.resolve('./static/src'),
      vue: 'vue/dist/vue.js',
    },
  },
  optimization: {
    minimizer: [
      new TerserPlugin({
        cache: true,
        parallel: true,
        sourceMap: true, // set to true if you want JS source maps
      }),
      new OptimizeCSSAssetsPlugin({}),
    ],
    splitChunks: {
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'initial',
        },
      },
    },
  },
  watchOptions: {
    aggregateTimeout: 300,
    poll: 1000,
  },
};
