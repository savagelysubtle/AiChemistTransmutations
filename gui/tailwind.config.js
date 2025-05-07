/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          background: '#0D1117',
          surface: '#161B22',
          border: '#30363d',
          primary: '#58A6FF',
          secondaryAccent: '#e94560',
          textPrimary: '#C9D1D9',
          textSecondary: '#8B949E',
          hoverPrimary: '#79C0FF',
        },
        light: {
          primary: '#ffffff',
          secondary: '#f7fafc',
          accent: '#e94560',
          text: '#2d3748',
          textSecondary: '#718096',
          border: '#e2e8f0',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
}