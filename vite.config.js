import { sentryVitePlugin } from "@sentry/vite-plugin";
import react from "@vitejs/plugin-react";
// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [
		react(),
		sentryVitePlugin({
			org: "seattle-beauty-lounge",
			project: "javascript",
		}),
	],

	root: "source/scripts",

	build: {
		sourcemap: true,
	},
});
