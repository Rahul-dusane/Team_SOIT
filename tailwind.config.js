/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: { ink: '#14252b', muted: '#6b7b82', line: '#e4eaeb', canvas: '#f7f9f8', mint: '#dff3e9', teal: '#14866d', coral: '#ef8b70' },
      fontFamily: { sans: ['Manrope', 'sans-serif'], display: ['DM Sans', 'sans-serif'] },
      boxShadow: { panel: '0 12px 40px rgba(20, 37, 43, .06)' },
    },
  },
  plugins: [],
}