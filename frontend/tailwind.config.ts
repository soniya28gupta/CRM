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
        crm: {
          blue: {
            DEFAULT: "#2563eb",
            hover: "#1d4ed8",
            light: "#eff6ff",
            dark: "#1e40af",
          },
          navy: {
            DEFAULT: "#0f172a",
            light: "#1e293b",
            muted: "#475569",
          },
          bg: {
            main: "#f8fafc",
            card: "#ffffff",
            subtle: "#f1f5f9",
            border: "#e2e8f0",
          },
        },
      },
    },
  },
  plugins: [],
};
export default config;

