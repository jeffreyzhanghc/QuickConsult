module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        'glow': 'glow 7s ease-in-out infinite',
        'glow-reverse': 'glow-reverse 7s ease-in-out infinite',
        'flow': 'flow 20s linear infinite',
        'flow-reverse': 'flow-reverse 25s linear infinite',
        'gradient-shift': 'gradient-shift 10s ease infinite alternate',
      },
      keyframes: {
        glow: {
          '0%, 100%': { 
            opacity: '0.8',
            transform: 'translate(0, 0) scale(1)'
          },
          '50%': { 
            opacity: '0.95',
            transform: 'translate(-2%, -2%) scale(1.05)'
          },
        },
        'glow-reverse': {
          '0%, 100%': { 
            opacity: '0.8',
            transform: 'translate(0, 0) scale(1)'
          },
          '50%': { 
            opacity: '0.95',
            transform: 'translate(2%, 2%) scale(1.05)'
          },
        },
        'flow': {
          '0%': { transform: 'rotate(0deg) scale(1.5)' },
          '50%': { transform: 'rotate(180deg) scale(1.3)' },
          '100%': { transform: 'rotate(360deg) scale(1.5)' },
        },
        'flow-reverse': {
          '0%': { transform: 'rotate(360deg) scale(1.5)' },
          '50%': { transform: 'rotate(180deg) scale(1.7)' },
          '100%': { transform: 'rotate(0deg) scale(1.5)' },
        },
        'gradient-shift': {
          '0%': {
            'background-size': '100% 100%',
            'background-position': '0% 0%',
          },
          '100%': {
            'background-size': '200% 200%',
            'background-position': '100% 100%',
          },
        },
      },
    },
  },
  plugins: [],
}