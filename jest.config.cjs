module.exports = {
	testEnvironment: "jsdom",
	testMatch: [
		"<rootDir>/admin/**/*.test.js",
		"<rootDir>/admin/**/*.test.jsx",
		"<rootDir>/source/scripts/**/*.test.js",
		"<rootDir>/source/scripts/**/*.test.jsx",
	],
	transform: {
		"^.+\\.[jt]sx?$": "babel-jest",
	},
	moduleNameMapper: {
		"^/rdp-style\\.css$": "<rootDir>/test/styleMock.js",
		"\\.(css)$": "<rootDir>/test/styleMock.js",
	},
	coverageDirectory: "<rootDir>/coverage/js",
	coverageReporters: ["json"],
	collectCoverageFrom: [
		"admin/**/*.js",
		"admin/**/*.jsx",
		"source/scripts/**/*.js",
		"source/scripts/**/*.jsx",
		"!admin/*-bootstrap.jsx",
		"!admin/**/*.test.js",
		"!source/scripts/**/*.test.js",
		"!source/scripts/**/*.test.jsx",
		"!source/scripts/*-bootstrap.jsx",
		"!source/scripts/booking-bootstrap.jsx",
		"!source/scripts/dist/**",
	],
	testPathIgnorePatterns: ["/node_modules/", "/source/scripts/dist/"],
	coveragePathIgnorePatterns: ["/node_modules/", "/source/scripts/dist/"],
	moduleFileExtensions: ["js", "jsx", "json"],
};
