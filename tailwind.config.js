/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        muted: '#64748b',
        line: '#e2e8f0',
        canvas: '#f8fafc',
        mint: '#ecfdf5',
        teal: '#0d9488',
        coral: '#f43f5e',
        apple: {
          blue: '#0071e3',
          dark: '#1d1d1f',
          zinc: '#f5f5f7',
          gray: '#86868b',
          light: '#fbfbfd'
        },
        napkin: {
          purple: '#6366f1',
          indigo: '#4f46e5',
          cyan: '#06b6d4',
          amber: '#f59e0b',
          emerald: '#10b981'
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'sans-serif']
      },
      boxShadow: {
        panel: '0 20px 40px -15px rgba(15, 23, 42, 0.05)',
        glass: '0 8px 32px 0 rgba(0, 0, 0, 0.04)',
        glow: '0 0 25px -5px rgba(0, 113, 227, 0.2)',
        'glow-purple': '0 0 25px -5px rgba(99, 102, 241, 0.25)',
        'apple-card': '0 4px 24px -2px rgba(0, 0, 0, 0.06)'
      },
      borderRadius: {
        '3xl': '1.5rem',
        '4xl': '2rem'
      }
    },
  },
  plugins: [],
}