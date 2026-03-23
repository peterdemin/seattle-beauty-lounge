import { afterEach, beforeEach, jest } from "@jest/globals";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import BookingWizard from "./BookingWizard.jsx";
import {
	addDays,
	formatDateForApi,
	formatDisplayDate,
} from "./bookingWizard/dateUtils.js";
import { mockJsonResponse } from "./testUtils/mockJsonResponse.js";

function installShell() {
	document.body.innerHTML = `
		<div id="service-table"></div>
		<div id="book-modal" class="hidden"></div>
		<button id="book-back" type="button">Back</button>
		<button id="book-close" type="button">Close</button>
		<button
			class="book-btn"
			type="button"
			data-service-id="svc-1"
			data-service-title="Custom Facial"
			data-duration="60"
		>
			Book now
		</button>
	`;
}

function getTomorrowAtNoon() {
	const date = addDays(new Date(), 1);
	date.setHours(12, 0, 0, 0);
	return date;
}

function formatDateForCalendarLabel(date) {
	return new Intl.DateTimeFormat("en-US", {
		month: "long",
		day: "numeric",
	}).format(date);
}

describe("BookingWizard", () => {
	beforeEach(() => {
		installShell();
		localStorage.clear();
	});

	afterEach(() => {
		document.body.innerHTML = "";
		jest.restoreAllMocks();
	});

	it("opens from document clicks, navigates back, and closes through the shell controls", async () => {
		global.fetch = jest.fn(() =>
			mockJsonResponse({
				"2026-03-16": [["10:00", "11:30"]],
			}),
		);

		render(<BookingWizard apiUrl="/api" />);

		const modal = document.getElementById("book-modal");
		const serviceTable = document.getElementById("service-table");
		const launchButton = document.querySelector(".book-btn");
		const backButton = document.getElementById("book-back");
		const closeButton = document.getElementById("book-close");

		expect(modal.classList.contains("hidden")).toBe(true);
		expect(serviceTable.classList.contains("hidden")).toBe(false);

		fireEvent.click(launchButton);

		expect(await screen.findByText("Pick a Date")).toBeTruthy();
		expect(modal.classList.contains("hidden")).toBe(false);
		expect(serviceTable.classList.contains("hidden")).toBe(true);

		fireEvent.click(backButton);
		await waitFor(() => {
			expect(screen.queryByText("Pick a Date")).toBeNull();
		});
		expect(modal.classList.contains("hidden")).toBe(false);
		expect(serviceTable.classList.contains("hidden")).toBe(false);

		fireEvent.click(backButton);
		await waitFor(() => {
			expect(modal.classList.contains("hidden")).toBe(true);
		});

		fireEvent.click(launchButton);
		expect(await screen.findByText("Pick a Date")).toBeTruthy();
		fireEvent.click(closeButton);
		await waitFor(() => {
			expect(modal.classList.contains("hidden")).toBe(true);
		});
	});

	it("walks through the booking flow and renders the confirmation state", async () => {
		const appointmentDate = getTomorrowAtNoon();
		const appointmentDateApi = formatDateForApi(appointmentDate);
		const appointmentDateLabel = formatDateForCalendarLabel(appointmentDate);
		const appointmentDateReview = formatDisplayDate(appointmentDateApi);

		global.fetch = jest
			.fn()
			.mockImplementationOnce(() =>
				mockJsonResponse({
					[appointmentDateApi]: [["10:00", "11:30"]],
				}),
			)
			.mockImplementationOnce(() =>
				mockJsonResponse({
					pubUrl: "https://example.com/appointments/abc",
				}),
			);

		render(<BookingWizard apiUrl="/api" />);

		fireEvent.click(document.querySelector(".book-btn"));

		fireEvent.click(
			await screen.findByRole("button", {
				name: new RegExp(appointmentDateLabel, "i"),
			}),
		);
		fireEvent.click(screen.getByRole("button", { name: "Next" }));

		expect(await screen.findByText("Pick a Time")).toBeTruthy();
		fireEvent.click(screen.getByRole("button", { name: "10:00 AM" }));
		fireEvent.click(screen.getByRole("button", { name: "Next" }));

		expect(await screen.findByText("Enter Your Information")).toBeTruthy();
		fireEvent.change(screen.getByLabelText("FULL NAME"), {
			target: { value: "Ada Lovelace" },
		});
		fireEvent.change(screen.getByLabelText("PHONE NUMBER"), {
			target: { value: "206-555-0101" },
		});
		fireEvent.change(screen.getByLabelText("E-MAIL"), {
			target: { value: "ada@example.com" },
		});
		fireEvent.click(
			screen.getByLabelText(/i consent to receive appointment reminders/i),
		);
		fireEvent.click(screen.getByRole("button", { name: "Next" }));

		expect(await screen.findByText("Review and Confirm")).toBeTruthy();
		expect(screen.getByText("Custom Facial")).toBeTruthy();
		expect(screen.getByText(appointmentDateReview)).toBeTruthy();
		expect(screen.getByText("10:00 AM")).toBeTruthy();

		fireEvent.click(screen.getByRole("button", { name: /confirm booking/i }));

		expect(await screen.findByText("Thank you, Ada Lovelace!")).toBeTruthy();
		expect(screen.getByText(/your appointment is confirmed/i)).toBeTruthy();
		expect(global.fetch).toHaveBeenNthCalledWith(
			2,
			"/api/appointments",
			expect.objectContaining({
				method: "POST",
			}),
		);
	});
});
