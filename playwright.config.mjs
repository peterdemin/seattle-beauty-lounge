import { defineConfig } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL;

export default defineConfig({
	testDir: "./tests/e2e",
	use: {
		baseURL: BASE_URL,
		trace: "retain-on-failure",
	},
	webServer: [],
});
