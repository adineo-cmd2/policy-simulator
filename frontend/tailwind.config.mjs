/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "navy": "#1e3a5f",
        "navydeep": "#142840",
        "navyedge": "#2c4f7c",
        "paper": "#ffffff",
        "parchment": "#f7f5ef",
        "gold": "#b45309",
        "goldsoft": "#f5e6cf",
        "inksoft": "#5b6b7f"
},
      fontFamily: {
        "display": [
                "'Spectral'",
                "Georgia",
                "serif"
        ],
        "body": [
                "'Libre Franklin'",
                "system-ui",
                "sans-serif"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ],
        "serif": [
                "'Spectral'",
                "Georgia",
                "serif"
        ],
        "sans": [
                "'Libre Franklin'",
                "system-ui",
                "sans-serif"
        ]
},
    },
  },
  plugins: [],
};
