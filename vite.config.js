import react from "@vitejs/plugin-react";
// import { sentryVitePlugin } from "@sentry/vite-plugin";
// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [
		react(),
		// sentryVitePlugin({ org: "seattle-beauty-lounge", project: "javascript"}),
	],
	server: {
		proxy: {
			"/api": {
				target: "http://127.0.0.1:8000",
				changeOrigin: false,
			},
		},
	},

	root: "source/scripts",

	build: {
		sourcemap: true,
		rollupOptions: {
			input: {
				appointment: "source/scripts/appointment.html",
				index: "source/scripts/index.html",
			},
		},
	},
});
