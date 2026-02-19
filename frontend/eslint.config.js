// eslint.config.js — ESLint v9 flat config (zero external dependencies)
// TypeScript files are checked by tsc --noEmit; ESLint only handles plain JS.
export default [
  {
    ignores: ["dist/**", "node_modules/**", "**/*.ts", "**/*.tsx"],
  },
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    rules: {
      "no-unused-vars": "warn",
      "no-console": "off",
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
    },
  },
];
