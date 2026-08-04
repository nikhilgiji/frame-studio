import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  envDir: "..",
  plugins: [react()],
  server: { port: 3000, host: "127.0.0.1" },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./tests/setup.ts",
    exclude: ["e2e/**", "node_modules/**", "dist/**"],
  },
});
