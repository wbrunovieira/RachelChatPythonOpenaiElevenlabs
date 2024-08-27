/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        customPurple1: '#350545',
        customPurple2: '#792990',
      },
    },
  },
  plugins: [],
};
