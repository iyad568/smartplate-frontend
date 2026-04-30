/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#143055",
          800: "#1b3a66",
        },
        brand: {
          red: "#e63946",
          gold: "#caa15a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "Segoe UI", "Tahoma", "sans-serif"],
        serif: ["Cormorant Garamond", "Georgia", "serif"],
        arabic: ["Tajawal", "Cairo", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
