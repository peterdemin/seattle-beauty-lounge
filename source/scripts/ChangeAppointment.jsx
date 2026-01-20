import React, { useState, useEffect, StrictMode } from "react";
import ReactDOM from "react-dom/client";

function ChangeAppointment({ apiUrl, appointmentId }) {
	const [data, setData] = useState(null);
	const [message, setMessage] = useState(null);

	useEffect(() => {
		if (!apiUrl) {
			return;
		}
		fetch(`${apiUrl}/appointment/${appointmentId}`)
			.then((res) => {
				if (res.ok) {
					return res.json();
				}
				res.text().then((text) => {
					setMessage(`Failed to fetch appointment details: ${text}`);
				});
				return null;
			})
			.then((json) => setData(json));
	}, [apiUrl, appointmentId]);

	return (
		<>
			{data && <FullAppointment data={data} />}
			{message && <div className="text-red-600">{message}</div>}
		</>
	);
}

function FullAppointment({ data }) {
	if (!data) {
		return null;
	}
	const date = new Date(`${data.date}T${data.time}`);
	const dateStr = new Intl.DateTimeFormat("en-US", {
		year: "numeric",
		month: "long",
		day: "numeric",
	}).format(date);
	const timeStr = new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);

	return (
		<div>
			<div className="flex flex-row text-xl mx-auto w-fit flex-wrap justify-items-start">
				<div className="flex flex-col text-xl mr-10">
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Date:</div>
						<div className="grow">{dateStr}</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Time:</div>
						<div className="grow">{timeStr}</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Service:</div>
						<div className="grow">{data.serviceTitle}</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Duration:</div>
						<div className="grow">{data.serviceDuration}</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Price:</div>
						<div className="grow">{data.servicePrice}</div>
					</div>
				</div>
			</div>
		</div>
	);
}

ReactDOM.createRoot(document.getElementById("appointment")).render(
	<StrictMode>
		<ChangeAppointment
			apiUrl="/api"
			appointmentId={new URLSearchParams(location.search).get("app")}
		/>
	</StrictMode>,
);
