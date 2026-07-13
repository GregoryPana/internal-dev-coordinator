/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#f8fafc",
        surface: "#ffffff",
        "surface-muted": "#f1f5f9",
        border: "#e2e8f0",
        text: "#0f172a",
        "muted-text": "#64748b",
        primary: {
          DEFAULT: "#0f766e",
          hover: "#115e59",
          fg: "#ffffff",
        },
        accent: "#0891b2",
        success: { DEFAULT: "#16a34a", bg: "#f0fdf4", border: "#bbf7d0" },
        warning: { DEFAULT: "#d97706", bg: "#fffbeb", border: "#fde68a" },
        danger: { DEFAULT: "#dc2626", bg: "#fef2f2", border: "#fecaca" },
        neutral: { DEFAULT: "#64748b", bg: "#f1f5f9", border: "#e2e8f0" },
      },
      borderRadius: {
        md: "10px",
        lg: "14px",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Inter",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
