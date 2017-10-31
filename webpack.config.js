const path = require('path');
const webpack = require('webpack');

function resolve(dir) {
  return path.join(__dirname, 'static', dir);
}

module.exports = {
  entry: resolve('src/js/index.js'),
  output: {
    path: resolve('dist'),
    filename: './js/site.js',
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        include: resolve('src/js'),
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        include: resolve('src/js'),
      },
      {
        test: /\.scss$/,
        use: [
          {
            loader: 'style-loader',
          },
          {
            loader: 'css-loader',
          },
          {
            loader: 'sass-loader',
          },
        ],
        include: resolve('src/scss'),
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        loader: 'file-loader',
        options: {
          name: 'images/[name].[ext]?[hash]',
        },
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.vue', '.json'],
    alias: {
      vue$: 'vue/dist/vue.esm.js',
      jquery: 'jquery/src/jquery',
      '@': resolve('src'),
    },
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
    }),
  ],
};
