import { afterEach, jest } from "@jest/globals";
import { render, screen } from "@testing-library/react";
import React from "react";

import ChangeAppointment from "./ChangeAppointment.jsx";
import { mockJsonResponse } from "./testUtils/mockJsonResponse.js";

describe("ChangeAppointment", () => {
	afterEach(() => {
		jest.restoreAllMocks();
	});

	it("renders fetched appointment details", async () => {
		global.fetch = jest.fn(() =>
			mockJsonResponse({
				serviceTitle: "Custom Facial",
				date: "2026-03-16",
				time: "10:00",
				serviceDuration: "60 min",
				servicePrice: "$120",
			}),
		);

		render(<ChangeAppointment apiUrl="/api" appointmentId="apt-1" />);

		expect(await screen.findByText("Custom Facial")).toBeTruthy();
		expect(screen.getByText("March 16, 2026")).toBeTruthy();
		expect(screen.getByText("10:00 AM")).toBeTruthy();
		expect(screen.getByText("60 min")).toBeTruthy();
		expect(screen.getByText("$120")).toBeTruthy();
	});

	it("shows the server error for failed loads", async () => {
		global.fetch = jest.fn(() => mockJsonResponse("not found", false, 404));

		render(<ChangeAppointment apiUrl="/api" appointmentId="missing" />);

		expect(
			await screen.findByText("Failed to fetch appointment details: not found"),
		).toBeTruthy();
	});
});
