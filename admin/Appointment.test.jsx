import { afterEach, jest } from "@jest/globals";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import { mockJsonResponse } from "../source/scripts/testUtils/mockJsonResponse.js";
import AdminDashboard, { buildSquarePaymentUrl } from "./Appointment.jsx";

describe("AdminDashboard", () => {
	afterEach(() => {
		jest.restoreAllMocks();
	});

	it("renders appointment details, history, and payment totals from fetched data", async () => {
		global.fetch = jest.fn(() =>
			mockJsonResponse({
				appointment: {
					id: "apt-1",
					clientName: "Ada Lovelace",
					clientPhone: "206-555-0101",
					clientEmail: "ada@example.com",
					date: "2026-03-16",
					time: "10:00",
					serviceId: "svc-1234",
					service: {
						title: "Custom Facial",
						duration: "60 min",
						price: "$120",
						price_cents: 12000,
					},
				},
				more: [
					{
						id: "apt-2",
						date: "2026-02-10",
						time: "09:15",
						serviceId: "svc-9999",
					},
				],
			}),
		);

		render(
			<AdminDashboard
				apiUrl="/admin/api"
				appointmentId="apt-1"
				clientId="client-123"
			/>,
		);

		expect(await screen.findByText("Ada Lovelace")).toBeTruthy();
		expect(screen.getByText(/svc-1234 - Custom Facial/)).toBeTruthy();
		expect(screen.getByText("March 16, 2026")).toBeTruthy();
		expect(screen.getByText("10:00 AM")).toBeTruthy();
		expect(screen.getByRole("link", { name: "206-555-0101" }).href).toContain(
			"tel:206-555-0101",
		);
		expect(screen.getByText("Appointment History")).toBeTruthy();
		expect(screen.getByRole("link", { name: "9:15 AM [svc-]" }).href).toContain(
			"?app=apt-2",
		);

		fireEvent.click(screen.getByRole("button", { name: "Charge" }));

		expect(screen.getByText("Pay for service")).toBeTruthy();
		expect(screen.getByText("Total: $120.00")).toBeTruthy();

		fireEvent.click(screen.getByText("20%"));
		expect(screen.getByText("Total: $144.00")).toBeTruthy();
	});

	it("shows the server error when appointment data cannot be fetched", async () => {
		global.fetch = jest.fn(() =>
			mockJsonResponse("missing appointment", false, 404),
		);

		render(
			<AdminDashboard
				apiUrl="/admin/api"
				appointmentId="missing"
				clientId="client-123"
			/>,
		);

		expect(
			await screen.findByText(
				"Failed to fetch appointment details: missing appointment",
			),
		).toBeTruthy();
	});
});

describe("buildSquarePaymentUrl", () => {
	afterEach(() => {
		jest.restoreAllMocks();
	});

	it("builds the Square deep link with the expected payment payload", () => {
		const url = buildSquarePaymentUrl("client-123", 14400, "tip included");

		expect(url.startsWith("square-commerce-v1://payment/create?data=")).toBe(
			true,
		);

		const encoded = url.split("data=")[1];
		const payload = JSON.parse(decodeURIComponent(encoded));
		expect(payload).toEqual({
			amount_money: {
				amount: 14400,
				currency_code: "USD",
			},
			callback_url: "https://seattle-beauty-lounge.com/confirm.html",
			client_id: "client-123",
			version: "1.3",
			notes: "tip included",
			options: {
				supported_tender_types: ["CREDIT_CARD"],
			},
		});
	});
});
