import React, { useState, useEffect, StrictMode } from "react";
import { DayPicker } from "react-day-picker";
import ReactDOM from "react-dom/client";
import "/rdp-style.css";
import * as Sentry from "@sentry/react";
import { CheckoutProvider } from "@stripe/react-stripe-js";
import { PaymentElement } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { useForm } from "react-hook-form";
import SquarePayment from "/SquarePayment.jsx";
import PayButton from "./PayButton.jsx";
import getAvailableSlots from "./availability.js";

function BookingWizard({
	apiUrl,
	stripePublishableKey,
	squareApplicationId,
	squareLocationId,
}) {
	const [currentStep, setCurrentStep] = useState(1);

	// Wizard State
	const [selectedServiceId, setSelectedServiceId] = useState(null);
	const [selectedServiceTitle, setSelectedServiceTitle] = useState(null);
	const [availability, setAvailability] = useState([]);
	const [duration, setDuration] = useState(null);
	const [slots, setSlots] = useState(null);
	const [selectedDate, setSelectedDate] = useState(null);
	const [selectedTime, setSelectedTime] = useState(null);
	const [clientName, setClientName] = useState(null);
	const [clientPhone, setClientPhone] = useState(null);
	const [clientEmail, setClientEmail] = useState(null);
	const [stripeClientSecret, setStripeClientSecret] = useState(null);

	const stripe = loadStripe(stripePublishableKey, {
		betas: ["custom_checkout_beta_5"],
	});

	useEffect(() => {
		fetch(`${apiUrl}/availability`)
			.then((response) => response.json())
			.then(setAvailability);
	}, [apiUrl]);

	useEffect(() => {
		if (duration === null || availability.length === 0) {
			return;
		}
		setSlots(getAvailableSlots(availability, duration));
	}, [availability, duration]);

	useEffect(() => {
		fetch(`${apiUrl}/checkout`, { method: "POST" })
			.then((response) => response.json())
			.then((json) => setStripeClientSecret(json.clientSecret));
	}, [apiUrl]);

	useEffect(() => {
		for (const element of document.getElementsByClassName("book-btn")) {
			element.addEventListener("click", () => {
				setSelectedServiceId(element.dataset.serviceId);
				setSelectedServiceTitle(element.dataset.serviceTitle);
				setDuration(element.dataset.duration);
				if (element.dataset.serviceId) {
					setCurrentStep(2);
				} else {
					setCurrentStep(1);
				}
				document.getElementById("book-modal").classList.remove("hidden");
			});
		}
		document.getElementById("book-close").addEventListener("click", () => {
			document.getElementById("book-modal").classList.add("hidden");
		});
	}, []);

	function handleSubmitAppointment(token) {
		fetch(`${apiUrl}/appointments`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				serviceId: selectedServiceId,
				date: selectedDate,
				time: selectedTime,
				clientName,
				clientPhone,
				clientEmail,
				token,
			}),
		}).then((res) => {
			if (res.ok) {
				setCurrentStep(99);
			} else {
				alert("Error submitting appointment");
			}
		});
	}

	const serviceTableEl = document.getElementById("service-table");
	if (serviceTableEl) {
		if (currentStep === 1) {
			document.getElementById("service-table").classList.remove("hidden");
		} else {
			document.getElementById("service-table").classList.add("hidden");
		}
	}

	// Render steps conditionally:
	return (
		<div>
			{currentStep === 2 && (
				<PickDateStep
					slots={slots}
					onDateSelect={(date) => {
						setSelectedDate(date);
						setCurrentStep(3);
					}}
				/>
			)}
			{currentStep === 3 && (
				<PickTimeslotStep
					slots={slots}
					date={selectedDate}
					onTimeslotSelect={(time) => {
						setSelectedTime(time);
						setCurrentStep(4);
					}}
				/>
			)}
			{currentStep === 4 && (
				<ClientInfoStep
					clientName={clientName}
					clientPhone={clientPhone}
					clientEmail={clientEmail}
					onNextStep={(name, phone, email) => {
						setClientName(name);
						setClientPhone(phone);
						setClientEmail(email);
						setCurrentStep(5);
					}}
				/>
			)}
			{currentStep === 5 && (
				<CheckoutStep
					clientEmail={clientEmail}
					clientSecret={stripeClientSecret}
					stripe={stripe}
					onConfirm={handleSubmitAppointment}
				/>
			)}
			<SquarePayment
				active={currentStep === 6}
				apiUrl={apiUrl}
				applicationId={squareApplicationId}
				locationId={squareLocationId}
				onPayment={handleSubmitAppointment}
			/>
			{currentStep === 7 && (
				<ReviewAndConfirmStep
					serviceTitle={selectedServiceTitle}
					date={selectedDate}
					time={selectedTime}
					clientName={clientName}
					clientPhone={clientPhone}
					clientEmail={clientEmail}
					onConfirm={handleSubmitAppointment}
				/>
			)}
			{currentStep === 99 && (
				<div class="mb-6">
					<h2 className="text-2xl text-center font-light text-primary">
						Thank you, {clientName}! Your appointment is confirmed.
					</h2>
					<p>
						You will receive an email confirmation at {clientEmail} with the
						booking details.
					</p>
					<p>We'll send a reminder the day before service to {clientPhone}</p>
					<p>
						To cancel or reschedule your appointment,
						<br />
						call{" "}
						<a
							class="font-medium text-primary underline"
							href="tel:+13016588708"
						>
							+1 (301) 658-8708
						</a>
					</p>
				</div>
			)}
		</div>
	);
}

function PickDateStep({ slots, onDateSelect }) {
	const [selectedDay, setSelectedDay] = useState(null);
	const [disabledDates, setDisabledDates] = useState(null);

	useEffect(() => {
		const dates = [];
		for (const dateStr in slots) {
			if (slots[dateStr].length === 0) {
				const [year, month, day] = dateStr.split("-").map(Number);
				dates.push(new Date(year, month - 1, day));
			}
		}
		setDisabledDates(dates);
	}, [slots]);

	function addDays(date, days) {
		const result = new Date(date);
		result.setDate(result.getDate() + days);
		return result;
	}

	const today = new Date();
	const first_day = addDays(today, 1); // next day
	const last_day = addDays(today, 7 * 6); // 6 weeks

	function handleNext() {
		if (selectedDay) {
			onDateSelect(selectedDay.toISOString().substring(0, 10));
		}
	}

	if (disabledDates === null) {
		return null;
	}

	return (
		<div>
			<h2 className="text-2xl text-center font-light text-primary">
				Pick a Date
			</h2>
			<DayPicker
				mode="single"
				selected={selectedDay}
				onSelect={setSelectedDay}
				// You can add optional props here, like `disabled` or `fromDate/toDate`
				// to limit the selectable date range.
				modifiers={{
					disabled: [{ before: first_day }, { after: last_day }].concat(
						disabledDates,
					),
				}}
			/>
			<NextButton handleNext={handleNext} disabled={!selectedDay} />
		</div>
	);
}

function NextButton({ handleNext, disabled }) {
	return (
		<div className="flex place-content-end">
			<button
				className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary
                   disabled:invisible
                   hover:bg-primary hover:text-neutral"
				onClick={handleNext}
				disabled={disabled}
				type="button"
			>
				Next
			</button>
		</div>
	);
}

function PickTimeslotStep({ slots, date, onTimeslotSelect }) {
	const [selected, setSelected] = useState(null);
	const [timeslots, setTimeslots] = useState([]);

	useEffect(() => {
		if (slots === null || date === null) {
			return;
		}
		setTimeslots(slots[date]);
	}, [slots, date]);

	const slotClass = (slot) => {
		const base = "cursor-pointer p-1 rounded-full border-2";
		if (selected === slot) {
			return `${base} border-primary text-primary`;
		}
		return `${base} border-neutral text-black`;
	};

	return (
		<div>
			<h2 className="text-2xl text-center pb-4 font-light text-primary">
				Pick a Time
			</h2>
			<div className="grid grid-cols-4 gap-4 mb-4">
				{timeslots.map((slot) => (
					<button
						onClick={() => {
							setSelected(slot);
						}}
						className={slotClass(slot)}
						type="button"
						key={slot}
					>
						{slot}
					</button>
				))}
			</div>
			<NextButton
				handleNext={() => {
					onTimeslotSelect(selected);
				}}
				disabled={!selected}
			/>
		</div>
	);
}

function ClientInfoStep({ clientName, clientPhone, clientEmail, onNextStep }) {
	const {
		register,
		handleSubmit,
		formState: { errors },
	} = useForm({
		defaultValues: {
			name: clientName,
			phone: clientPhone,
			email: clientEmail,
		},
	});

	const onSubmit = (data) => {
		onNextStep(data.name, data.phone, data.email);
	};

	const labelClass = "block mt-2 font-light text-primary";
	const inputClass =
		"block bg-neutral border border-primary text-black text-sm rounded-lg focus:ring-primary w-full p-2.5";

	return (
		<form onSubmit={handleSubmit(onSubmit)}>
			<h2 className="text-2xl text-center pb-4 font-light text-primary">
				Enter Your Information
			</h2>

			<div>
				<label htmlFor="name" className={labelClass}>
					FULL NAME
				</label>
				<input
					id="name"
					className={inputClass}
					{...register("name", { required: "Name is required" })}
					placeholder="Your Full Name"
				/>
				{errors.name && <p style={{ color: "red" }}>{errors.name.message}</p>}
			</div>

			<div>
				<label htmlFor="phone" className={labelClass}>
					PHONE NUMBER
				</label>
				<input
					id="phone"
					className={inputClass}
					{...register("phone", {
						required: "Phone number is required",
						pattern: {
							value: /^[\d\s()+-]+$/,
							message: "Invalid phone format",
						},
					})}
					placeholder="e.g. 555-123-4567"
				/>
				{errors.phone && <p style={{ color: "red" }}>{errors.phone.message}</p>}
			</div>

			<div class="mb-4">
				<label htmlFor="email" className={labelClass}>
					E-MAIL
				</label>
				<input
					id="email"
					className={inputClass}
					{...register("email", {
						required: "Email is required",
						pattern: {
							value: /^[^@]+@[^@]+\.[^@]+$/,
							message: "Invalid email format",
						},
					})}
					placeholder="you@example.com"
				/>
				{errors.email && <p style={{ color: "red" }}>{errors.email.message}</p>}
			</div>

			<div className="mt-4 flex place-content-end">
				<button
					className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary
                    hover:bg-primary hover:text-neutral"
					type="submit"
				>
					Next
				</button>
			</div>
		</form>
	);
}

function ReviewAndConfirmStep({
	serviceTitle,
	date,
	time,
	clientName,
	clientPhone,
	clientEmail,
	onConfirm,
}) {
	function formatDate(date) {
		const dayOfWeek = date.toLocaleString("en-US", { weekday: "long" });
		const month = date.toLocaleString("en-US", { month: "long" });
		const day = date.getDate();
		return `${dayOfWeek}, ${month} ${day}`;
	}
	return (
		<div>
			<h2 className="text-2xl text-center font-light text-primary mb-4">
				Review and Confirm
			</h2>
			<p className="text-lg font-light [&>span]:font-medium [&>span]:text-primary">
				I, <span>{clientName}</span>, want to book <span>{serviceTitle}</span>{" "}
				on <span>{formatDate(date)}</span> at <span>{time}</span>.
			</p>
			<p className="text-lg font-light [&>span]:font-medium [&>span]:text-primary">
				You can contact me by phone: <span>{clientPhone}</span>
			</p>
			<p className="text-lg font-light [&>span]:font-medium [&>span]:text-primary">
				Or by email: <span>{clientEmail}</span>
			</p>
			<div className="flex place-content-center my-4">
				<button
					className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary"
					onClick={onConfirm}
					type="button"
				>
					Confirm Booking
				</button>
			</div>
		</div>
	);
}

const CheckoutStep = ({ clientEmail, clientSecret, onConfirm, stripe }) => {
	if (!clientSecret) {
		return null;
	}
	return (
		<CheckoutProvider
			stripe={stripe}
			options={{
				clientSecret,
				elementsOptions: {
					appearance: {
						theme: "night",
						variables: {
							colorPrimary: "#0dc0ca",
							colorBackground: "#ffe8cb",
							colorText: "#000000",
							colorDanger: "#df1b41",
							spacingUnit: "2px",
							borderRadius: "4px",
						},
					},
				},
			}}
		>
			<form>
				<PaymentElement options={{ layout: "accordion" }} />
				<PayButton email={clientEmail} onConfirm={onConfirm} />
			</form>
		</CheckoutProvider>
	);
};

if (import.meta.env.VITE_SENTRY_DSN) {
	Sentry.init({
		dsn: import.meta.env.VITE_SENTRY_DSN,
		integrations: [
			Sentry.browserTracingIntegration(),
			Sentry.replayIntegration(),
		],
		// Tracing
		tracesSampleRate: 1.0, //  Capture 100% of the transactions
		tracePropagationTargets: [
			"http://127.0.0.1:8000/index.html",
			"https://staging.seattle-beauty-lounge.com/",
		],
		// Session Replay
		replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
		replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
		debug: true,
	});
}

ReactDOM.createRoot(document.getElementById("book")).render(
	<StrictMode>
		<BookingWizard
			apiUrl={import.meta.env.VITE_API_URL}
			stripePublishableKey={import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY}
			squareApplicationId={import.meta.env.VITE_SQUARE_APPLICATION_ID}
			squareLocationId={import.meta.env.VITE_SQUARE_LOCATION_ID}
		/>
	</StrictMode>,
);

export default BookingWizard;
