/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#06B6D4',
        secondary: '#059669',
        accent: '#10B981',
      },
    },
  },
  plugins: [],
}
