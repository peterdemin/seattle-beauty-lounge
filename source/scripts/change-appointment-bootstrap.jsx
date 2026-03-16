import React, { StrictMode } from "react";
import ReactDOM from "react-dom/client";

import ChangeAppointment from "./ChangeAppointment.jsx";

ReactDOM.createRoot(document.getElementById("appointment")).render(
	<StrictMode>
		<ChangeAppointment
			apiUrl="/api"
			appointmentId={new URLSearchParams(location.search).get("app")}
		/>
	</StrictMode>,
);
