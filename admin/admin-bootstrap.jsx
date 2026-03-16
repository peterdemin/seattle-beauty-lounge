import React, { StrictMode } from "react";
import ReactDOM from "react-dom/client";

import AdminDashboard from "./Appointment.jsx";

ReactDOM.createRoot(document.getElementById("admin")).render(
	<StrictMode>
		<AdminDashboard
			apiUrl="/admin/api"
			clientId={import.meta.env.VITE_SQUARE_APPLICATION_ID}
			appointmentId={new URLSearchParams(location.search).get("app")}
		/>
	</StrictMode>,
);
