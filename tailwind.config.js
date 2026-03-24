/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
      },
      boxShadow: {
        hud: "0 30px 90px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.18)",
        glow: "0 0 0 1px rgba(255,255,255,.14), 0 25px 70px rgba(0,0,0,.35)",
      },
      keyframes: {
        "float-y": {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
        },
        "shimmer-x": {
          "0%": { transform: "translateX(-30%)" },
          "100%": { transform: "translateX(30%)" },
        },
      },
      animation: {
        "float-y": "float-y 3.6s ease-in-out infinite",
        "shimmer-x": "shimmer-x 2.8s ease-in-out infinite",
      },
      colors: {
        hud: {
          glass: "rgba(255,255,255,.10)",
          border: "rgba(255,255,255,.18)",
        },
      },
    },
  },
  plugins: [],
}
