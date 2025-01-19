import React, { useState, useEffect, StrictMode } from "react";
import ReactDOM from "react-dom/client";

function AdminDashboard({ apiUrl, appointmentId }) {
	const [data, setData] = useState(null);

	useEffect(() => {
		if (!apiUrl) {
			return;
		}
		fetch(`${apiUrl}/admin/appointment/${appointmentId}`)
			.then((res) => res.json())
			.then((json) => setData(json));
	}, [apiUrl, appointmentId]);

	return (
		<>
			{data !== null && (
				<>
					<FullAppointment data={data.appointment} />
					<AppointmentHistory data={data.more} />
				</>
			)}
		</>
	);
}

function FullAppointment({ data }) {
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
						<li key="{item.id}" className="w-20 text-right">
							<a href={`?app=${item.id}`}>{formatTime(item.time)}</a>
						</li>
					));
					return (
						<div key={day} className="flex items-baseline">
							<div className="text-lg w-10 text-right shrink-0 pr-4">{day}</div>
							<ul className="flex grow flex-wrap pl-2 border-l-2 border-black">
								{timeElems}
							</ul>
						</div>
					);
				});
				return (
					<div key={month} className="flex items-baseline">
						<div className="text-lg shrink-0 w-24">{month}</div>
						<ul>{dayElems}</ul>
					</div>
				);
			},
		);
		return (
			<div key={year} className="flex pr-5 items-baseline">
				<div className="text-xl w-20">{year}</div>
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

ReactDOM.createRoot(document.getElementById("admin")).render(
	<StrictMode>
		<AdminDashboard
			apiUrl="/api" // {import.meta.env.VITE_API_URL}
			appointmentId={new URLSearchParams(location.search).get("app")}
		/>
	</StrictMode>,
);
