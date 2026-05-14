import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          ink: "#111827",
          teal: "#0f766e",
          sky: "#38bdf8",
          mint: "#ccfbf1",
          danger: "#dc2626",
          paper: "#f8fafc"
        }
      },
      boxShadow: {
        panel: "0 14px 42px rgba(15, 23, 42, 0.10)"
      }
    }
  },
  plugins: [],
};

export default config;
