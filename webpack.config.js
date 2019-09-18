const path = require("path");
const glob = require("glob");

module.exports = {
  mode: 'production',
  entry: {
    "bundle.js": glob.sync("build/static/js/*.js").map(f => path.resolve(__dirname, f)),
  },
  output: {
    filename: 'bundle.min.js',
    path: __dirname + '/libretto/static/js/',
  },
};
