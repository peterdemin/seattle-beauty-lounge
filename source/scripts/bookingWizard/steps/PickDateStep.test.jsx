import { afterEach, beforeEach, jest } from "@jest/globals";
import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";

import PickDateStep from "./PickDateStep.jsx";

describe("PickDateStep", () => {
	beforeEach(() => {
		jest.useFakeTimers();
		jest.setSystemTime(new Date("2026-03-15T12:00:00Z"));
	});

	afterEach(() => {
		jest.useRealTimers();
	});

	it("shows loading and error states", () => {
		const { rerender } = render(
			<PickDateStep slots={null} isLoading error="" onDateSelect={() => {}} />,
		);

		expect(screen.getByText("Loading availability...")).toBeTruthy();

		rerender(
			<PickDateStep
				slots={null}
				isLoading={false}
				error="Failed to load availability"
				onDateSelect={() => {}}
			/>,
		);

		expect(screen.getByText("Failed to load availability")).toBeTruthy();
	});

	it("lets the user pick a date and continues with an API-friendly value", () => {
		const onDateSelect = jest.fn();

		render(
			<PickDateStep
				slots={{
					"2026-03-16": ["10:00 AM"],
					"2026-03-17": [],
				}}
				isLoading={false}
				error=""
				onDateSelect={onDateSelect}
			/>,
		);

		fireEvent.click(screen.getByRole("button", { name: /march 16/i }));
		fireEvent.click(screen.getByRole("button", { name: "Next" }));

		expect(onDateSelect).toHaveBeenCalledWith("2026-03-16");
	});
});
