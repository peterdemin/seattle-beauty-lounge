/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./admin/admin.html", "./admin/*.jsx"],
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
