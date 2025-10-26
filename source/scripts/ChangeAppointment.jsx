import React, { useState, useEffect, StrictMode } from "react";
import ReactDOM from "react-dom/client";

function ChangeAppointment({ apiUrl, appointmentId, clientId }) {
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
			{message && <div className="text-red-600">{message}</div>}
		</>
	);
}

function FullAppointment({ data, clientId }) {
	if (!data) {
		return null;
	}
	const [paymentActive, setPaymentActive] = useState(false);
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
					onClick={() => setPaymentActive(true)}
					type="button"
				>
					Charge
				</button>
				<PaymentForm
					clientId={clientId}
					service={data.service}
					active={paymentActive}
				/>
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

function PaymentForm({ clientId, service, active }) {
	const [tip, setTip] = useState(0);
	const hidden = active ? "" : "hidden ";
	const modalClass = `${hidden} overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 flex flex-col md:justify-center items-center w-full h-full md:bg-opacity-90 bg-primary`;
	const subtotal = (service.price_cents - 5000) / 100;
	const total = (subtotal + (service.price_cents * tip) / 10000).toFixed(2);
	const tipClass =
		"p-4 mx-2 border-2 rounded-lg text-center basis-1/4 font-bold";
	const activeTipClass = `bg-primary text-neutral border-primary ${tipClass}`;
	const inactiveTipClass = `border-black text-black ${tipClass}`;
	return (
		<div tabindex="-1" aria-hidden="true" className={modalClass}>
			<div className="relative mx-auto my-auto p-4 w-full md:max-w-3xl md:h-fit bg-neutral md:rounded-lg md:shadow">
				<div className="flex items-center justify-between p-4 md:p-5 rounded-t">
					<h2 className="w-full my-2 lg:text-5xl text-3xl font-medium leading-tight text-center text-primary">
						Pay for service
					</h2>
					<button
						id="book-close"
						type="button"
						className="text-primary bg-transparent hover:bg-primary hover:text-neutral rounded-full text-sm w-8 h-8 ms-auto inline-flex justify-center items-center"
						data-modal-hide="default-modal"
					>
						<svg
							className="w-3 h-3"
							aria-hidden="true"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 14 14"
						>
							<path
								stroke="currentColor"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
							/>
						</svg>
						<span className="sr-only">Cancel</span>
					</button>
				</div>
				<div className="max-w-xl mx-auto text-black text-2xl">
					<div>Service price: {service.price}</div>
					<div>Deposit: -$50</div>
					<div>Subtotal: ${subtotal}</div>
					<div className="text-3xl py-4 text-center w-full font-light">
						Add tip
					</div>
					<div className="py-4 flex justify-between place-items-center">
						<button
							className={tip === 15 ? activeTipClass : inactiveTipClass}
							type="button"
							onClick={() => setTip(15)}
						>
							15%
						</button>
						<button
							className={tip === 20 ? activeTipClass : inactiveTipClass}
							type="button"
							onClick={() => setTip(20)}
						>
							20%
						</button>
						<button
							className={tip === 25 ? activeTipClass : inactiveTipClass}
							type="button"
							onClick={() => setTip(25)}
						>
							25%
						</button>
						<button
							className={inactiveTipClass}
							type="button"
							onClick={() => setTip(0)}
						>
							No tip
						</button>
					</div>

					<div className="flex items-center place-content-end py-8">
						<div className="font-bold">Total: ${total}</div>
						<button
							className="ml-8 px-6 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary drop-shadow-lg"
							onClick={() => payInApp(clientId, total * 100, "")}
							type="button"
						>
							Pay
						</button>
					</div>
				</div>
			</div>
		</div>
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

ReactDOM.createRoot(document.getElementById("appointment")).render(
	<StrictMode>
		<ChangeAppointment
			apiUrl="/api"
			clientId={import.meta.env.VITE_SQUARE_APPLICATION_ID}
			appointmentId={new URLSearchParams(location.search).get("app")}
		/>
	</StrictMode>,
);
