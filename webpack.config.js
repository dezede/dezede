const path = require("path");

module.exports = {
  mode: 'production',
  entry: path.resolve(__dirname, 'src/index.tsx'),
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    filename: 'bundle.min.js',
    path: path.resolve(__dirname, 'libretto/static/js/'),
  },
};
