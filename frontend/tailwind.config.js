/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: {
          950: "#07090E",
          900: "#0C101A",
          850: "#111726",
          800: "#171F33",
          700: "#222D47",
        },
        violet: {
          500: "#8B5CF6",
          600: "#7C3AED",
          glow: "rgba(139, 92, 246, 0.35)",
        },
        electric: {
          500: "#3B82F6",
          400: "#60A5FA",
          glow: "rgba(59, 130, 246, 0.35)",
        },
        cyan: {
          400: "#22D3EE",
          500: "#06B6D4",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        display: ["Outfit", "Inter", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 35px -5px rgba(139, 92, 246, 0.3)",
        "glow-cyan": "0 0 30px -5px rgba(6, 182, 212, 0.3)",
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "scan-line": "scan 2s linear infinite",
      },
      keyframes: {
        scan: {
          "0%": { top: "0%" },
          "100%": { top: "100%" },
        }
      }
    },
  },
  plugins: [],
}
