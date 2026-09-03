/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          900: "#312e81",
        },
        slate: {
          850: "#151e2e",
          950: "#0b0f19",
        },
        evidence: {
          green: "#10b981",
          amber: "#f59e0b",
          red: "#ef4444",
          cyan: "#06b6d4",
          purple: "#a855f7"
        }
      },
    },
  },
  plugins: [],
};
