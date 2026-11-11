import { defineConfig } from "vite";

// Relative URLs work on GitHub Pages project sites (/<repository>/) and on /.
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    target: "es2022",
    sourcemap: false,
    assetsInlineLimit: 0,
  },
});
