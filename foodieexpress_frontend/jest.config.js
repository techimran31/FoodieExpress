module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/foodieexpress_frontend/tests'],
  testMatch: ['**/*.test.js'],
  moduleFileExtensions: ['js', 'mjs'],
  transform: {
    '^.+\\.m?js$': ['babel-jest', { presets: [['@babel/preset-env', { targets: { node: 'current' } }]] }],
  },
  moduleNameMapper: {
    '^(\\.\\/.*\\.js)$': '$1',
  },
  testTimeout: 10000,
};