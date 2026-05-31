import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(240 10% 6%)",
        foreground: "hsl(30 12% 94%)",
        card: "hsl(240 8% 10%)",
        "card-foreground": "hsl(30 12% 94%)",
        primary: "hsl(35 84% 62%)",
        "primary-foreground": "hsl(240 10% 6%)",
        muted: "hsl(240 8% 18%)",
        "muted-foreground": "hsl(30 7% 72%)",
        border: "hsl(240 8% 22%)",
        accent: "hsl(35 40% 26%)",
        ring: "hsl(35 84% 62%)"
      },
      boxShadow: {
        luxe: "0 8px 40px rgba(0, 0, 0, 0.45)"
      },
      borderRadius: {
        xl: "1rem"
      }
    }
  },
  plugins: []
};

export default config;
