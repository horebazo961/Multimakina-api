import type { Config } from "tailwindcss"
export default { content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"], theme: { extend: { fontFamily: { sans: ["Manrope", "sans-serif"], mono: ["DM Mono", "monospace"] }, colors: { ink: "#07101d", panel: "#0d1a2a", line: "#1d334a", signal: "#35e0a1", amber: "#f8c15c" } } }, plugins: [] } satisfies Config
