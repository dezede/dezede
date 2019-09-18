const {
  override,
  addDecoratorsLegacy,
  disableEsLint,
} = require('customize-cra');

module.exports = override(
  // enable legacy decorators babel plugin
  addDecoratorsLegacy(),

  // disable eslint in webpack
  disableEsLint(),
);
