/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./script.js"],
  theme: {
    extend: {
      fontFamily: {
        headline: ["Newsreader", "serif"],
        body: ["Manrope", "sans-serif"],
        sans: ["Manrope", "sans-serif"],
      },
      colors: {
        primary: "#271310",
        secondary: "#79564b",
        tertiary: "#24150f",
        surface: "#f9f9f9",
        "surface-container": "#eeeeee",
        "surface-container-low": "#f3f3f3",
        "surface-container-high": "#e8e8e8",
        "surface-container-highest": "#e2e2e2",
        "surface-container-lowest": "#ffffff",
        "on-surface": "#1a1c1c",
        "on-surface-variant": "#504442",
        "outline-variant": "#d3c3c0",
        "secondary-container": "#fed0c1",
        "on-secondary-container": "#79574c",
        "tertiary-fixed": "#fadcd2",
        "on-tertiary-fixed-variant": "#56423b",
        error: "#ba1a1a",
      },
      transitionProperty: {
        "max-height": "max-height",
      },
    },
  },
  plugins: [],
};
