const path = require('path');

function resolve(rest) {
  return path.join(__dirname, rest);
}

exports.resolve = resolve;

exports.cssLoaders = (options) => {
  options = options || {};
  const cssLoader = {
    loader: 'css-loader',
    options: {
      minimize: process.env.NODE_ENV === 'production',
      sourceMap: options.sourceMap,
    },
  };
  function generateLoaders(loader, loaderOptions) {
    const loaders = [cssLoader];
    if (loader) {
      loaders.push({
        loader: `${loader}-loader`,
        options: Object.assign({}, loaderOptions, {
          sourceMap: options.sourceMap,
        }),
      });
    }
    if (options.extracter) {
      return options.extracter.extract({
        use: loaders,
        fallback: 'style-loader',
      });
    }
    return ['style-loader'].concat(loaders);
  }
  return {
    css: generateLoaders(),
    scss: generateLoaders('sass'),
  };
};

exports.styleLoaders = (options) => {
  const output = [];
  const loaders = exports.cssLoaders(options);
  Object.keys(loaders).forEach((extension) => {
    const loader = loaders[extension];
    output.push({
      test: new RegExp(`\\.${extension}$`),
      use: loader,
      include: resolve('src/scss'),
    });
  });
  return output;
};
