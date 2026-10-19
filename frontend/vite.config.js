import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendProxy = {
  target: "http://127.0.0.1:8001",
  changeOrigin: true,
  secure: false,
};

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/chat": backendProxy,
      "/models": backendProxy,
    },
  },
});
