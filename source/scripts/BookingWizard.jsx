import React, { useState, useEffect, StrictMode } from "react";
import { DayPicker } from "react-day-picker";
import ReactDOM from "react-dom/client";
import "/rdp-style.css";
import { CheckoutProvider } from "@stripe/react-stripe-js";
import { PaymentElement, useCheckout } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { useForm } from "react-hook-form";
import PayButton from "./PayButton.jsx";

function BookingWizard({ apiUrl, stripePublishableKey }) {
	const [currentStep, setCurrentStep] = useState(2);

	// Wizard State
	const [availability, setAvailability] = useState([]);
	const [selectedService, setSelectedService] = useState(null);
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
		async function fetchAvailability() {
			// const res = await fetch(`${apiUrl}/availability`);
			// const data = await res.json();
			const data = [
				{
					id: "id",
					name: "name",
					description: "description",
				},
			];
			setAvailability(data);
		}
		fetchAvailability();

		fetch(`${apiUrl}/checkout`, { method: "POST" })
			.then((response) => response.json())
			.then((json) => setStripeClientSecret(json.clientSecret));

		for (const element of document.getElementsByClassName("book-btn")) {
			element.addEventListener("click", () => {
				setSelectedService(element.dataset.serviceId);
				setCurrentStep(2);
				document.getElementById("book-modal").classList.remove("hidden");
			});
		}
		document.getElementById("book-close").addEventListener("click", () => {
			document.getElementById("book-modal").classList.add("hidden");
		});
	}, [apiUrl]);

	async function handleSubmitAppointment() {
		const payload = {
			serviceId: selectedService,
			date: selectedDate.toISOString().substring(0, 10),
			time: selectedTime,
			clientName,
			clientPhone,
			clientEmail,
		};

		const res = await fetch(`${apiUrl}/appointments`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(payload),
		});

		if (res.ok) {
			// Success - show confirmation
			setCurrentStep("confirmation");
		} else {
			// Handle errors
			alert("Error submitting appointment");
		}
	}

	// Render steps conditionally:
	return (
		<div>
			{currentStep === 2 && (
				<PickDateStep
					onDateSelect={(date) => {
						setSelectedDate(date);
						setCurrentStep(3);
					}}
				/>
			)}
			{currentStep === 3 && (
				<PickTimeslotStep
					serviceId={selectedService}
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
					clientPhone={clientPhone}
					clientEmail={clientEmail}
					clientSecret={stripeClientSecret}
					stripe={stripe}
					onConfirm={handleSubmitAppointment}
				/>
			)}
			{currentStep === 6 && (
				<ReviewAndConfirmStep
					serviceId={selectedService}
					date={selectedDate}
					time={selectedTime}
					clientName={clientName}
					clientPhone={clientPhone}
					clientEmail={clientEmail}
					onConfirm={handleSubmitAppointment}
				/>
			)}
			{currentStep === "confirmation" && (
				<div>
					<h2 className="text-2xl text-center font-thin text-amber-300">
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
							class="font-medium text-amber-300 underline"
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

function PickDateStep({ onDateSelect }) {
	const [selectedDay, setSelectedDay] = useState(null);

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
			onDateSelect(selectedDay);
		}
	}

	return (
		<div>
			<h2 className="text-2xl text-center font-thin text-amber-300">
				Pick a Date
			</h2>
			<DayPicker
				mode="single"
				selected={selectedDay}
				onSelect={setSelectedDay}
				// You can add optional props here, like `disabled` or `fromDate/toDate`
				// to limit the selectable date range.
				modifiers={{
					disabled: [
						{ dayOfWeek: [0] },
						{ before: first_day },
						{ after: last_day },
						new Date(2024, 11, 30),
						new Date(2024, 11, 31),
						new Date(2025, 0, 1),
					],
				}}
			/>
			<div className="flex place-content-end">
				<button
					className="py-2 px-5 rounded-lg text-2xl text-amber-300 font-bold border-2 border-amber-300
                       disabled:invisible
                       hover:bg-amber-300 hover:text-black"
					onClick={handleNext}
					disabled={!selectedDay}
					type="button"
				>
					Next
				</button>
			</div>
		</div>
	);
}

function PickTimeslotStep({ serviceId, date, onTimeslotSelect }) {
	const [selected, setSelected] = useState(null);
	const [timeslots, setTimeslots] = useState([]);

	useEffect(() => {
		async function fetchTimes() {
			const isoDate = date.toISOString().substring(0, 10);
			const response = await fetch(
				`${apiUrl}/availability?service=${serviceId}&date=${isoDate}`,
			);
			// const data = await response.json();
			const data = [
				"07:00",
				"07:15",
				"07:30",
				"07:45",
				"08:00",
				"08:15",
				"08:30",
				"08:45",
				"09:00",
				"09:15",
				"09:30",
				"09:45",
			];
			setTimeslots(data);
		}
		fetchTimes();
	}, [serviceId, date]);

	const slotClass = (slot) => {
		const base = "cursor-pointer p-1 rounded-full border-2";
		if (selected === slot) {
			return `${base} border-amber-300 text-amber-300`;
		}
		return `${base} border-black text-white`;
	};

	return (
		<div>
			<h2 className="text-2xl text-center pb-4 font-thin text-amber-300">
				Pick a Time
			</h2>
			<div className="grid grid-cols-4 gap-4">
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
			<div className="mt-4 flex place-content-end">
				<button
					className="py-2 px-5 rounded-lg text-2xl text-amber-300 font-bold border-2 border-amber-300
                    disabled:invisible
                    hover:bg-amber-300 hover:text-black"
					onClick={() => {
						onTimeslotSelect(selected);
					}}
					disabled={!selected}
					type="button"
				>
					Next
				</button>
			</div>
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

	const labelClass = "block mt-2 font-thin text-amber-300";
	const inputClass =
		"block bg-stone-700 border border-amber-600 text-white text-sm rounded-lg focus:ring-amber-300 focus:border-amber-500 w-full p-2.5";

	return (
		<form onSubmit={handleSubmit(onSubmit)}>
			<h2 className="text-2xl text-center pb-4 font-thin text-amber-300">
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

			<div>
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
					className="py-2 px-5 rounded-lg text-2xl text-amber-300 font-bold border-2 border-amber-300
                 hover:bg-amber-300 hover:text-black"
					type="submit"
				>
					Next
				</button>
			</div>
		</form>
	);
}

function ReviewAndConfirmStep({
	serviceId,
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
			<h2 className="text-2xl text-center font-thin text-amber-300 mb-4">
				Review and Confirm
			</h2>
			<p className="text-lg font-thin [&>span]:font-medium [&>span]:text-amber-300">
				I, <span>{clientName}</span>, want to book <span>{serviceId}</span> on{" "}
				<span>{formatDate(date)}</span> at <span>{time}</span>.
			</p>
			<p className="text-lg font-thin [&>span]:font-medium [&>span]:text-amber-300">
				You can contact me by phone: <span>{clientPhone}</span>
			</p>
			<p className="text-lg font-thin [&>span]:font-medium [&>span]:text-amber-300">
				Or by email: <span>{clientEmail}</span>
			</p>
			<div className="flex place-content-center my-4">
				<button
					className="py-2 px-5 rounded-lg text-2xl text-amber-300 font-bold border-2 border-amber-300 hover:bg-amber-300 hover:text-black"
					onClick={onConfirm}
					type="button"
				>
					Confirm Booking
				</button>
			</div>
		</div>
	);
}

const CheckoutStep = ({
	clientPhone,
	clientEmail,
	clientSecret,
	onConfirm,
	stripe,
}) => {
	if (clientSecret) {
		return (
			<CheckoutProvider
				stripe={stripe}
				options={{
					clientSecret,
					elementsOptions: {
						appearance: {
							theme: "night",
							variables: {
								colorPrimary: "#fcd34d",
								colorBackground: "#000000",
								colorText: "#d1d5db",
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
	}
	return null;
};

ReactDOM.createRoot(document.getElementById("book")).render(
	<StrictMode>
		<BookingWizard
			apiUrl="https://api.staging.seattle-beauty-lounge.com"
			// apiUrl="http://localhost:8000"
			stripePublishableKey="pk_test_51Qalad4JEQklJs336eRXneul1QBSEn00GJ2AwYLKQcIKha0QoB53KOnPJtFUY2r5kAcGM5ltfn9qFqRNAXEQQBX20077lrDx0t"
		/>
	</StrictMode>,
);

export default BookingWizard;
