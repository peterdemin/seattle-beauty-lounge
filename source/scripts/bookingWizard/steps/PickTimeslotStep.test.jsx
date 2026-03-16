import { jest } from "@jest/globals";
import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import PickTimeslotStep from "./PickTimeslotStep.jsx";

describe("PickTimeslotStep", () => {
	it("renders available times and submits the selected slot", () => {
		const onTimeslotSelect = jest.fn();

		render(
			<PickTimeslotStep
				slots={{
					"2026-03-16": ["10:00 AM", "10:30 AM", "11:00 AM"],
				}}
				date="2026-03-16"
				onTimeslotSelect={onTimeslotSelect}
			/>,
		);

		const nextButton = screen.getByRole("button", { name: "Next" });
		expect(nextButton.disabled).toBe(true);

		fireEvent.click(screen.getByRole("button", { name: "10:30 AM" }));
		expect(nextButton.disabled).toBe(false);

		fireEvent.click(nextButton);
		expect(onTimeslotSelect).toHaveBeenCalledWith("10:30 AM");
	});
});
