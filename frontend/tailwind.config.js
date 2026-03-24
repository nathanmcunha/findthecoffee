/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./script.js"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#e0c8c1',
          500: '#e05d3a', 
          600: '#c24b2e',
          900: '#3a2b27',
        }
      },
      backgroundImage: {
        'card-header-gradient': 'linear-gradient(135deg, #fdf8f6 0%, #f2e8e5 100%)',
      },
      transitionProperty: {
        'max-height': 'max-height',
      }
    }
  },
  plugins: [],
}
