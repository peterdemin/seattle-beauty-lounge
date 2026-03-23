import { jest } from "@jest/globals";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import ClientInfoStep from "./ClientInfoStep.jsx";

describe("ClientInfoStep", () => {
	it("shows form validation and submits entered client info", async () => {
		const onNextStep = jest.fn();

		render(
			<ClientInfoStep
				client={{
					name: "Ada Lovelace",
					phone: "206-555-0101",
					email: "ada@example.com",
				}}
				onNextStep={onNextStep}
			/>,
		);

		expect(screen.getByLabelText("FULL NAME").value).toBe("Ada Lovelace");
		expect(screen.getByLabelText("PHONE NUMBER").value).toBe("206-555-0101");
		expect(screen.getByLabelText("E-MAIL").value).toBe("ada@example.com");

		const nextButton = screen.getByRole("button", { name: "Next" });
		expect(nextButton.disabled).toBe(true);

		fireEvent.click(nextButton);
		expect(onNextStep).not.toHaveBeenCalled();
		expect(screen.queryByText("Invalid email format")).toBeNull();

		fireEvent.change(screen.getByLabelText("E-MAIL"), {
			target: { value: "not-an-email" },
		});
		fireEvent.click(
			screen.getByLabelText(/i consent to receive appointment reminders/i),
		);
		expect(nextButton.disabled).toBe(false);
		fireEvent.click(nextButton);

		expect(await screen.findByText("Invalid email format")).toBeTruthy();
		expect(onNextStep).not.toHaveBeenCalled();

		fireEvent.change(screen.getByLabelText("FULL NAME"), {
			target: { value: "Ada Lovelace" },
		});
		fireEvent.change(screen.getByLabelText("PHONE NUMBER"), {
			target: { value: "206-555-0101" },
		});
		fireEvent.change(screen.getByLabelText("E-MAIL"), {
			target: { value: "ada@example.com" },
		});
		fireEvent.click(nextButton);

		await waitFor(() => {
			expect(onNextStep).toHaveBeenCalled();
		});

		expect(onNextStep.mock.calls[0][0]).toEqual({
			name: "Ada Lovelace",
			phone: "206-555-0101",
			email: "ada@example.com",
		});
	});
});
