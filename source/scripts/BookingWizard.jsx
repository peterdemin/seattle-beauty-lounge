import React, { useEffect, useLayoutEffect } from "react";
import "/rdp-style.css";

import renderConfirmation from "./ConfirmationTemplate.js";
import { STEP } from "./bookingWizard/constants.js";
import ClientInfoStep from "./bookingWizard/steps/ClientInfoStep.jsx";
import PickDateStep from "./bookingWizard/steps/PickDateStep.jsx";
import PickTimeslotStep from "./bookingWizard/steps/PickTimeslotStep.jsx";
import ReviewAndConfirmStep from "./bookingWizard/steps/ReviewAndConfirmStep.jsx";
import {
	getServiceFromElement,
	useBookingWizard,
} from "./bookingWizard/useBookingWizard.js";

function BookingWizard({ apiUrl }) {
	const { state, availability, actions } = useBookingWizard({ apiUrl });

	useEffect(() => {
		const modal = document.getElementById("book-modal");
		if (modal) {
			modal.classList.toggle("hidden", !state.isOpen);
		}
		const serviceTable = document.getElementById("service-table");
		if (serviceTable) {
			serviceTable.classList.toggle("hidden", state.step !== STEP.SERVICE);
		}
	}, [state.isOpen, state.step]);

	useLayoutEffect(() => {
		function handleDocumentClick(event) {
			const target = event.target instanceof Element ? event.target : null;
			if (!target) {
				return;
			}

			const button = target.closest(".book-btn");
			if (button instanceof HTMLElement) {
				actions.open(getServiceFromElement(button));
				return;
			}

			if (target.closest("#book-close")) {
				actions.close();
				return;
			}

			if (target.closest("#book-back")) {
				if (state.step === STEP.SERVICE) {
					actions.close();
					return;
				}
				actions.back();
			}
		}

		document.addEventListener("click", handleDocumentClick);
		return () => {
			document.removeEventListener("click", handleDocumentClick);
		};
	}, [actions, state.step]);

	return (
		<div>
			{state.step === STEP.DATE && (
				<PickDateStep
					slots={availability.slots}
					isLoading={availability.isAvailabilityLoading}
					error={availability.availabilityError}
					onDateSelect={actions.selectDate}
				/>
			)}
			{state.step === STEP.TIME && (
				<PickTimeslotStep
					key={state.selectedDate ?? "time"}
					slots={availability.slots}
					date={state.selectedDate}
					onTimeslotSelect={actions.selectTime}
				/>
			)}
			{state.step === STEP.CLIENT && (
				<ClientInfoStep client={state.client} onNextStep={actions.saveClient} />
			)}
			{state.step === STEP.REVIEW && (
				<ReviewAndConfirmStep
					serviceTitle={state.service?.title ?? ""}
					date={state.selectedDate}
					time={state.selectedTime}
					client={state.client}
					error={state.submitError}
					onConfirm={actions.confirm}
				/>
			)}
			{state.step === STEP.CONFIRMED && (
				<div
					className="mb-6"
					dangerouslySetInnerHTML={{
						__html: renderConfirmation(
							state.client.name,
							state.client.email,
							state.client.phone,
							state.pubUrl,
						),
					}}
				/>
			)}
		</div>
	);
}

export default BookingWizard;
