// /** @type {import('tailwindcss').Config} */
// export default {
//   content: [
//     "./index.html",
//     "./src/**/*.{js,ts,jsx,tsx}",
//   ],
//   theme: {
//     extend: {
//       colors: {
//         primary: {
//           50: '#f5f3ff',
//           100: '#ede9fe',
//           200: '#ddd6fe',
//           300: '#c4b5fd',
//           400: '#a78bfa',
//           500: '#8b5cf6',
//           600: '#7c3aed',
//           700: '#6d28d9',
//           800: '#5b21b6',
//           900: '#4c1d95',
//         },
//       },
//       animation: {
//         'fade-in': 'fadeIn 0.3s ease-out',
//         'slide-up': 'slideUp 0.3s ease-out',
//         'pulse-dot': 'pulseDot 1.4s infinite ease-in-out',
//       },
//       keyframes: {
//         fadeIn: {
//           '0%': { opacity: '0', transform: 'translateY(10px)' },
//           '100%': { opacity: '1', transform: 'translateY(0)' },
//         },
//         slideUp: {
//           '0%': { opacity: '0', transform: 'translateY(20px)' },
//           '100%': { opacity: '1', transform: 'translateY(0)' },
//         },
//         pulseDot: {
//           '0%, 80%, 100%': { opacity: '0.3', transform: 'scale(0.8)' },
//           '40%': { opacity: '1', transform: 'scale(1)' },
//         },
//       },
//     },
//   },
//   plugins: [],
// }


/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fffbeb', // Very light gold background
          100: '#fef3c7', // Light gold
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b', // Main Gold Accent (replaces purple 500)
          600: '#d97706', // Darker gold
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-dot': 'pulseDot 1.4s infinite ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseDot: {
          '0%, 80%, 100%': { opacity: '0.3', transform: 'scale(0.8)' },
          '40%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}