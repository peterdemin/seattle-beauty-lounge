import React, { useState, useEffect, StrictMode } from "react";
import ReactDOM from "react-dom/client";

function AdminDashboard({ apiUrl, appointmentId, clientId }) {
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
			{data && (
				<>
					<FullAppointment data={data.appointment} clientId={clientId} />
					<AppointmentHistory data={data.more} />
				</>
			)}
			{message && <div class="text-red-600">{message}</div>}
		</>
	);
}

function FullAppointment({ data, clientId }) {
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
						<div className="flex-0 shrink-0 w-24 font-medium">Name:</div>
						<div className="grow">{data.clientName}</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Phone:</div>
						<div className="grow">
							<a href={`tel:${data.clientPhone}`}>{data.clientPhone}</a>
						</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Email:</div>
						<div className="grow">
							<a href={`mailto:${data.clientEmail}`}>{data.clientEmail}</a>
						</div>
					</div>
				</div>
				<div className="flex flex-col text-xl mr-10">
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Date:</div>
						<div className="grow">{dateStr}</div>
					</div>
					<div className="flex flex-row">
						<div className="flex-0 shrink-0 w-24 font-medium">Time:</div>
						<div className="grow">{timeStr}</div>
					</div>
				</div>
				{data.service && (
					<div className="flex flex-col text-xl">
						<div className="flex flex-row">
							<div className="flex-0 shrink-0 w-24 font-medium">Service:</div>
							<div className="grow">
								{data.serviceId} - {data.service.title}
							</div>
						</div>
						<div className="flex flex-row">
							<div className="flex-0 shrink-0 w-24 font-medium">Duration:</div>
							<div className="grow">{data.service.duration}</div>
						</div>
						<div className="flex flex-row">
							<div className="flex-0 shrink-0 w-24 font-medium">Price:</div>
							<div className="grow">{data.service.price}</div>
						</div>
					</div>
				)}
				<button
					className="ml-8 px-6 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary"
					onClick={() => payInApp(clientId, data.service.price_cents, "")}
					type="button"
				>
					Pay
				</button>
			</div>
		</div>
	);
}

function AppointmentHistory({ data }) {
	function groupBy(dates, keyfunc) {
		const grouped = [];
		let curKey = null;
		for (const [date, item] of dates) {
			const key = keyfunc(date);
			if (key !== curKey) {
				grouped.push([key, []]);
				curKey = key;
			}
			grouped[grouped.length - 1][1].push([date, item]);
		}
		return grouped;
	}

	function groupDatesByYear(dates) {
		return groupBy(dates, (date) => date.getFullYear());
	}

	function groupDatesByMonth(dates) {
		return groupBy(dates, (date) =>
			new Intl.DateTimeFormat("en-US", { month: "long" }).format(date),
		);
	}

	function groupDatesByDate(dates) {
		return groupBy(dates, (date) => date.getDate() + 1);
	}

	function formatTime(timeStr) {
		const d = new Date();
		const [hours, minutes, _] = timeStr.split(":").map(Number);
		d.setHours(hours);
		d.setMinutes(minutes);
		const formatter = new Intl.DateTimeFormat("en-US", {
			hour: "numeric",
			minute: "numeric",
			hour12: true,
		});
		return formatter.format(d);
	}

	const dates = data.map((item) => [new Date(item.date), item]);
	const dateBreakdown = groupDatesByYear(dates).map(([year, yearItems]) => {
		const monthElems = groupDatesByMonth(yearItems).map(
			([month, monthItems]) => {
				const dayElems = groupDatesByDate(monthItems).map(([day, dayItems]) => {
					const timeElems = dayItems.map(([_, item]) => (
						<a
							key="{item.id}"
							className="w-24 text-right font-mono mb-4 mr-4 p-2"
							href={`?app=${item.id}`}
						>
							{formatTime(item.time)} [{item.serviceId.substr(0, 4)}]
						</a>
					));
					return (
						<div key={day} className="flex items-baseline">
							<div className="text-lg w-10 text-right shrink-0 pr-4 font-mono">
								{day}
							</div>
							<ul className="flex grow flex-wrap pl-2 border-l-2 border-black">
								{timeElems}
							</ul>
						</div>
					);
				});
				return (
					<div key={month} className="flex items-baseline">
						<div className="text-lg shrink-0 w-fit px-2">{month}</div>
						<ul>{dayElems}</ul>
					</div>
				);
			},
		);
		return (
			<div key={year} className="flex pr-5 items-baseline">
				<div className="text-xl w-fit pr-2">{year}</div>
				<ul>{monthElems}</ul>
			</div>
		);
	});

	return (
		<>
			<h2 className="text-3xl font-light pt-10 pb-5">Appointment History</h2>
			<ul className="w-fit mx-auto flex flex-col">{dateBreakdown}</ul>
		</>
	);
}

function payInApp(clientId, amountCents, notes) {
	window.location =
		// biome-ignore lint/style/useTemplate: this looks nicer
		"square-commerce-v1://payment/create?data=" +
		encodeURIComponent(
			JSON.stringify({
				amount_money: {
					amount: amountCents,
					currency_code: "USD",
				},
				callback_url: "https://seattle-beauty-lounge.com/confirm.html",
				client_id: clientId,
				version: "1.3",
				notes: notes,
				options: {
					supported_tender_types: ["CREDIT_CARD"],
				},
			}),
		);
}

ReactDOM.createRoot(document.getElementById("admin")).render(
	<StrictMode>
		<AdminDashboard
			apiUrl="/admin/api"
			clientId={import.meta.env.VITE_SQUARE_APPLICATION_ID}
			appointmentId={new URLSearchParams(location.search).get("app")}
		/>
	</StrictMode>,
);
