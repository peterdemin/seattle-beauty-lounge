import React, { StrictMode } from "react";
import reactDom from "react-dom/client";
import BookingWizard from "./BookingWizard.jsx";
import { initBookingSentry } from "./bookingSentry.js";

initBookingSentry(import.meta.env.VITE_SENTRY_DSN || "");

reactDom.createRoot(document.getElementById("book")).render(
	<StrictMode>
		<BookingWizard apiUrl={import.meta.env.VITE_API_URL || "/api"} />
	</StrictMode>,
);
