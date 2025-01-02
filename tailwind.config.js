/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./.build/index.html", "./source/scripts/*.{js,jsx,ts,tsx}"],
	theme: {
		extend: {
			colors: {
				primary: "#0dc0ca",
				secondary: "#e9cf3d",
			},
		},
	},
	plugins: [require("tailwindcss-neumorphism")],
};
