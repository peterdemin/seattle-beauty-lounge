import { jest } from "@jest/globals";
import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import ReviewAndConfirmStep from "./ReviewAndConfirmStep.jsx";

describe("ReviewAndConfirmStep", () => {
	it("shows booking details and confirms the booking", () => {
		const onConfirm = jest.fn();

		render(
			<ReviewAndConfirmStep
				serviceTitle="Custom Facial"
				date="2026-03-16"
				time="10:00 AM"
				client={{
					name: "Ada Lovelace",
					phone: "206-555-0101",
					email: "ada@example.com",
				}}
				error="Time slot unavailable"
				onConfirm={onConfirm}
			/>,
		);

		expect(screen.getByText("Custom Facial")).toBeTruthy();
		expect(screen.getByText("Monday, March 16")).toBeTruthy();
		expect(screen.getByText("Time slot unavailable")).toBeTruthy();

		fireEvent.click(screen.getByRole("button", { name: /confirm booking/i }));
		expect(onConfirm).toHaveBeenCalled();
	});
});
