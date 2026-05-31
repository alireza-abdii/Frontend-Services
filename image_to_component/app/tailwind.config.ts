import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(240 10% 6%)",
        foreground: "hsl(30 12% 94%)",
        card: "hsl(240 8% 10%)",
        border: "hsl(240 8% 22%)",
        primary: "hsl(35 84% 62%)",
        muted: "hsl(240 8% 18%)",
        "muted-foreground": "hsl(30 7% 72%)"
      },
      boxShadow: {
        luxe: "0 8px 40px rgba(0, 0, 0, 0.45)"
      }
    }
  },
  plugins: []
} satisfies Config;
