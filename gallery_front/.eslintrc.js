module.exports = {
  root: true,

  env: {
    node: true
  },

  extends: [
    '@vue/standard',
    'plugin:vue/recommended'
  ],

  parserOptions: {
    parser: 'babel-eslint',
    sourceType: 'module'
  },

  rules: {
    'no-console': 'off',
    'no-debugger': 'off',
    'vue/valid-v-html': 'off'
  }
}
