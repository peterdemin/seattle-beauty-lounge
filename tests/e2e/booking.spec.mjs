import { expect, test } from "@playwright/test";
import { BookingPage } from "./pages/booking-page.mjs";
import {
	assertHasAvailability,
	buildAvailableSlotsByDate,
	pickRandomSlot,
} from "./support/availability.mjs";

test("books an appointment using live backend", async ({ page, request }) => {
	const booking = new BookingPage(page);
	const customer = {
		name: "peter",
		phone: "2403421438",
		email: "peter@seattle-beauty-lounge.com",
	};

	await booking.clearSessionState();
	await booking.open();
	await booking.openServiceSelection();
	const durationMinutes = await booking.selectFirstService();

	const availability = await request.get("/api/availability");
	expect(availability.ok()).toBeTruthy();
	const availabilityData = await availability.json();
	const availableByDate = buildAvailableSlotsByDate(
		availabilityData,
		durationMinutes,
	);
	expect(assertHasAvailability(availableByDate).length).toBeGreaterThan(0);

	const randomSlot = pickRandomSlot(availableByDate);
	await booking.selectDate(randomSlot.date);

	await booking.proceedToNextStep();
	await booking.goToStepText("Pick a Time");
	await booking.pickRandomTime();
	await booking.proceedToNextStep();

	await booking.fillCustomerInfo(customer);
	await booking.proceedToNextStep();

	await booking.confirmBooking();
	await booking.assertAppointmentConfirmed(customer.name);
});
