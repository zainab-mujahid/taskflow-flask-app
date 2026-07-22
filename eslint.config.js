const js = require("@eslint/js");

// The app ships plain, un-bundled browser scripts (app/static/js/*.js) loaded
// via <script> tags, not ES modules or a build step, so this lints them as
// classic browser scripts and declares the small set of globals they share
// with each other through `window` (see app/static/js/api.js and toast.js).
module.exports = [
  js.configs.recommended,
  {
    files: ["app/static/js/**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "script",
      globals: {
        window: "readonly",
        document: "readonly",
        localStorage: "readonly",
        fetch: "readonly",
        FormData: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        confirm: "readonly",
        console: "readonly",
        apiFetch: "readonly",
        showToast: "readonly",
      },
    },
    rules: {
      "no-unused-vars": ["warn", { args: "none" }],
    },
  },
];
