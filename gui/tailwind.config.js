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
          surfaceElevated: '#21262D',
          border: '#30363d',
          borderSubtle: '#21262D',
          primary: '#58A6FF',
          primaryHover: '#79C0FF',
          primaryPressed: '#388BFD',
          secondaryAccent: '#e94560',
          textPrimary: '#C9D1D9',
          textSecondary: '#8B949E',
          textMuted: '#6E7681',
          hoverPrimary: '#79C0FF',
          // Status colors
          success: '#3FB950',
          successBg: '#0D4429',
          warning: '#D29922',
          warningBg: '#3D2914',
          error: '#F85149',
          errorBg: '#490202',
          info: '#58A6FF',
          infoBg: '#0C2D6B',
          // Gradient colors
          gradientStart: '#58A6FF',
          gradientEnd: '#E94560',
        },
        light: {
          background: '#FFFFFF',
          surface: '#F8F9FA',
          surfaceElevated: '#FFFFFF',
          border: '#E1E4E8',
          borderSubtle: '#F6F8FA',
          primary: '#0969DA',
          primaryHover: '#0860CA',
          primaryPressed: '#0550AE',
          secondaryAccent: '#E94560',
          textPrimary: '#24292F',
          textSecondary: '#656D76',
          textMuted: '#8B949E',
          hoverPrimary: '#0860CA',
          // Status colors
          success: '#1A7F37',
          successBg: '#DCFCE7',
          warning: '#9A6700',
          warningBg: '#FEF3C7',
          error: '#D1242F',
          errorBg: '#FEE2E2',
          info: '#0969DA',
          infoBg: '#DDF4FF',
          // Gradient colors
          gradientStart: '#0969DA',
          gradientEnd: '#E94560',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'bounce-subtle': 'bounceSubtle 0.6s ease-in-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(88, 166, 255, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(88, 166, 255, 0.6)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}