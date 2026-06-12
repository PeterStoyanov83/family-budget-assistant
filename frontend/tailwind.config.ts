import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2D6A4F",
          foreground: "#ffffff",
          50: "#e8f5f0",
          100: "#c5e8d8",
          500: "#2D6A4F",
          600: "#245a42",
          700: "#1c4835",
        },
        promo: {
          real: "#52B788",
          average: "#F4A261",
          fake: "#E63946",
        },
      },
      borderRadius: {
        DEFAULT: "12px",
        lg: "12px",
        md: "8px",
        sm: "4px",
      },
    },
  },
  plugins: [],
};

export default config;
