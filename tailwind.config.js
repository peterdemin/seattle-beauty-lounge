/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./.build/index.html", "./source/scripts/*.{js,jsx,ts,tsx}"],
	theme: {
		extend: {
			colors: {
				primary: "rgb(var(--color-primary))",
				secondary: "rgb(var(--color-secondary))",
				neutral: "rgb(var(--color-neutral))",
			},
		},
	},
	plugins: [],
};
