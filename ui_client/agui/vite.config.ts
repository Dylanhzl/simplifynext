import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // The React app and the static fallback share one stylesheet in
    // ui_client/static, so Vite needs to read one level above the app root.
    fs: { allow: [".."] },
    proxy: {
      // Default dev path: talk to the UI server on :8000, which is either
      // replaying fixtures or proxying the live CDR agent on :8084.
      "/ag-ui": { target: "http://localhost:8000", changeOrigin: true },
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
  build: { outDir: "dist", sourcemap: true },
});
