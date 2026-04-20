/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        drug: { light: '#dbeafe', border: '#3b82f6', text: '#1d4ed8' },
        symptom: { light: '#fed7aa', border: '#f97316', text: '#c2410c' },
        dosage: { light: '#d1fae5', border: '#10b981', text: '#065f46' },
      },
    },
  },
  plugins: [],
}
