import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // все запросы вида /processing/* будут проксированы на vul-pes.ru:2998/processing/*
      "/processing": {
        target: "http://vul-pes.ru:2998",
        changeOrigin: true,
        secure: false,
        // rewrite: path => path.replace(/^\/processing/, '/processing')
      },
    },
  },
});
