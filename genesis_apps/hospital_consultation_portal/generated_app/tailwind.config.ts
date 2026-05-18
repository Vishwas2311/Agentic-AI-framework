import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          50:  "#f0fdfb",
          100: "#ccfbf5",
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#2BB5A0",
          700: "#1D8A77",
          800: "#0f766e",
          900: "#134e4a",
        },
        navy: {
          DEFAULT: "#1B3A5C",
          light: "#2D5282",
        },
        surface: {
          DEFAULT: "#F0F4F8",
          card:    "#FFFFFF",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
