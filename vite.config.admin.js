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
		rollupOptions: {
			input: {
				app: "admin/admin.html",
			},
		},
	},
	server: {
		open: "/admin.html",
		proxy: {
			"/admin": "http://localhost:8000",
		},
	},
});
