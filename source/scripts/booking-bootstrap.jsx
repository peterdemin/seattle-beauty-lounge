import React, { StrictMode } from "react";
import reactDom from "react-dom/client";
import BookingWizard from "./BookingWizard.jsx";

reactDom.createRoot(document.getElementById("book")).render(
	<StrictMode>
		<BookingWizard apiUrl={import.meta.env.VITE_API_URL || "/api"} />
	</StrictMode>,
);
