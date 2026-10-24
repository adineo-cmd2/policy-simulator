/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        navy: '#1e3a5f',
        navydeep: '#142840',
        navyedge: '#2c4f7c',
        paper: '#ffffff',
        parchment: '#f7f5ef',
        gold: '#b45309',
        goldsoft: '#f5e6cf',
        inksoft: '#5b6b7f',
      },
      fontFamily: {
        serif: ['Georgia', '"Times New Roman"', 'serif'],
        sans: ['system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
