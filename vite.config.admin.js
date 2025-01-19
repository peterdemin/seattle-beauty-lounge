import react from "@vitejs/plugin-react";
// import { sentryVitePlugin } from "@sentry/vite-plugin";
// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [
		react(),
		// sentryVitePlugin({
		// 	org: "seattle-beauty-lounge",
		// 	project: "javascript",
		// }),
	],

	root: "admin",

	build: {
		sourcemap: true,
	},
	server: {
		proxy: {
			"/api": "http://localhost:8000",
		},
	},
});
