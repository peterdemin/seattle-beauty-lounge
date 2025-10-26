import react from "@vitejs/plugin-react";
// import { sentryVitePlugin } from "@sentry/vite-plugin";
// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [
		react(),
		// sentryVitePlugin({ org: "seattle-beauty-lounge", project: "javascript"}),
	],

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
