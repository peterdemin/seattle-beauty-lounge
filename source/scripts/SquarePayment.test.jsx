import { afterEach, beforeEach, jest } from "@jest/globals";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import SquarePayment from "./SquarePayment.jsx";

const mockPayments = jest.fn();

jest.mock("@square/web-sdk", () => ({
	payments: (...args) => mockPayments(...args),
}));

describe("SquarePayment", () => {
	beforeEach(() => {
		mockPayments.mockReset();
		jest.restoreAllMocks();
	});

	afterEach(() => {
		jest.restoreAllMocks();
	});

	it("loads the Square card, tokenizes, and forwards the payment to the callback", async () => {
		const attach = jest.fn(() => Promise.resolve());
		const destroy = jest.fn();
		const tokenize = jest.fn(() =>
			Promise.resolve({ status: "OK", token: "tok-success" }),
		);
		const card = { attach, destroy, tokenize };
		const paymentApi = {
			card: jest.fn(() => Promise.resolve(card)),
		};
		mockPayments.mockResolvedValue(paymentApi);
		const onPayment = jest.fn(() => Promise.resolve(null));

		const { unmount } = render(
			<SquarePayment
				applicationId="app-id"
				locationId="loc-id"
				active
				onPayment={onPayment}
			/>,
		);

		const payButton = await screen.findByRole("button", { name: "Pay $50" });
		expect(payButton).toBeTruthy();
		expect(mockPayments).toHaveBeenCalledWith("app-id", "loc-id");
		await waitFor(() => {
			expect(paymentApi.card).toHaveBeenCalledWith({});
			expect(attach).toHaveBeenCalled();
			expect(payButton.disabled).toBe(false);
		});

		fireEvent.click(payButton);

		await waitFor(() => {
			expect(onPayment).toHaveBeenCalledWith({
				idempotencyKey: expect.any(String),
				token: "tok-success",
			});
		});
		expect(onPayment.mock.calls[0][0].idempotencyKey).toHaveLength(8);

		unmount();
		expect(destroy).toHaveBeenCalled();
	});

	it("shows booking callback failures to the user", async () => {
		const attach = jest.fn(() => Promise.resolve());
		const tokenize = jest.fn(() =>
			Promise.resolve({ status: "OK", token: "tok-failure" }),
		);
		const paymentApi = {
			card: jest.fn(() =>
				Promise.resolve({ attach, destroy: jest.fn(), tokenize }),
			),
		};
		mockPayments.mockResolvedValue(paymentApi);
		const onPayment = jest.fn(() => Promise.resolve("Card declined"));
		const consoleErrorSpy = jest
			.spyOn(console, "error")
			.mockImplementation(() => {});

		render(
			<SquarePayment
				applicationId="app-id"
				locationId="loc-id"
				active
				onPayment={onPayment}
			/>,
		);

		const payButton = await screen.findByRole("button", { name: "Pay $50" });
		await waitFor(() => {
			expect(payButton.disabled).toBe(false);
		});
		fireEvent.click(payButton);

		expect(
			await screen.findByText(
				"Failed to book an appointment. Error: Card declined",
			),
		).toBeTruthy();
		expect(consoleErrorSpy).toHaveBeenCalledWith("Card declined");
	});

	it("shows tokenization errors and stays hidden when inactive", async () => {
		const attach = jest.fn(() => Promise.resolve());
		const tokenize = jest.fn(() =>
			Promise.resolve({
				status: "INVALID",
				errors: [{ message: "Card details are invalid" }],
			}),
		);
		const paymentApi = {
			card: jest.fn(() =>
				Promise.resolve({ attach, destroy: jest.fn(), tokenize }),
			),
		};
		mockPayments.mockResolvedValue(paymentApi);
		const onPayment = jest.fn(() => Promise.resolve(null));

		const { container } = render(
			<SquarePayment
				applicationId="app-id"
				locationId="loc-id"
				active={false}
				onPayment={onPayment}
			/>,
		);

		expect(container.firstChild.className).toContain("hidden");

		const payButton = await screen.findByRole("button", { name: "Pay $50" });
		await waitFor(() => {
			expect(payButton.disabled).toBe(false);
		});
		fireEvent.click(payButton);

		expect(
			await screen.findByText(
				"Payment failed with status: INVALID. Error: Card details are invalid",
			),
		).toBeTruthy();
		expect(onPayment).not.toHaveBeenCalled();
	});
});
