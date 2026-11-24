/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");

module.exports = {
  darkMode: "class",
  content: ["./templates/**/*.html", "./**/templates/**/*.html"],
  safelist: [
    "badge",
    "badge-slate",
    "badge-blue",
    "badge-amber",
    "badge-green",
    "badge-red",
  ],
  theme: {
    extend: {
      colors: {
        brand: colors.indigo,
        accent: colors.orange,
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
