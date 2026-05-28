import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 0 1px rgba(99, 102, 241, 0.25), 0 0 30px rgba(79, 70, 229, 0.35)",
      },
    },
  },
  plugins: [],
}

export default config

