/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta AESA
        'aesa': {
          blue: '#1B95C8',
          'blue-dark': '#0F4F73',
          'blue-light': '#4FB3DB',
        },
        // Neutros estilo Apple
        neutral: {
          white: '#FFFFFF',
          light: '#F5F7F8',
          cream: '#F1EFEA',
          'text-secondary': '#6B7280',
          'text-primary': '#1F2933',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        'aesa': '12px',
        'aesa-lg': '16px',
      },
      boxShadow: {
        'aesa': '0 4px 12px rgba(15, 79, 115, 0.15)',
        'aesa-sm': '0 2px 8px rgba(15, 79, 115, 0.1)',
        'glass': '0 8px 32px rgba(15, 79, 115, 0.08)',
      },
      backdropBlur: {
        'aesa': '12px',
      },
      transitionDuration: {
        'aesa': '200ms',
      },
    },
  },
  plugins: [],
}
