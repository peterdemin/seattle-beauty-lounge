import React from "react";
import { useForm } from "react-hook-form";

function ClientInfoStep({ client, onNextStep }) {
	const {
		register,
		handleSubmit,
		formState: { errors },
	} = useForm({
		defaultValues: {
			name: client.name,
			phone: client.phone,
			email: client.email,
		},
	});

	const labelClass = "block mt-2 font-light text-primary";
	const inputClass =
		"block bg-neutral border border-primary text-black text-sm rounded-lg focus:ring-primary w-full p-2.5";

	return (
		<form onSubmit={handleSubmit(onNextStep)}>
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
				{errors.name && <p className="text-red-600">{errors.name.message}</p>}
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
				{errors.phone && <p className="text-red-600">{errors.phone.message}</p>}
			</div>

			<div className="mb-4">
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
				{errors.email && <p className="text-red-600">{errors.email.message}</p>}
			</div>

			<div className="flex gap-2 justify-baseline">
				<input
					type="checkbox"
					id="consent"
					name="consent"
					value="yes"
					required
					className="appearance-none w-6 h-6 rounded-full border border-primary bg-neutral mt-1 shrink-0 checked:bg-primary checked:border-0"
				/>
				<label htmlFor="consent">
					I consent to receive appointment reminders via email and text.
				</label>
			</div>

			<div className="mt-4 flex place-content-end">
				<button
					className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary hover:bg-primary hover:text-neutral"
					type="submit"
				>
					Next
				</button>
			</div>
		</form>
	);
}

export default ClientInfoStep;
