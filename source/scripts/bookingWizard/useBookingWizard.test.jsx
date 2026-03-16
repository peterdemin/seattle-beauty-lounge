import { afterEach, jest } from "@jest/globals";
import { act, renderHook, waitFor } from "@testing-library/react";

import { mockJsonResponse } from "../testUtils/mockJsonResponse.js";
import { STEP } from "./constants.js";
import { getServiceFromElement, useBookingWizard } from "./useBookingWizard.js";

describe("useBookingWizard", () => {
	afterEach(() => {
		localStorage.clear();
		jest.restoreAllMocks();
	});

	it("hydrates client info from localStorage and computes slots after service selection", async () => {
		global.fetch = jest.fn(() =>
			mockJsonResponse({
				"2026-03-20": [["10:00", "11:30"]],
			}),
		);
		localStorage.setItem("clientName", "Ada");
		localStorage.setItem("clientPhone", "206-555-0101");
		localStorage.setItem("clientEmail", "ada@example.com");

		const { result } = renderHook(() => useBookingWizard({ apiUrl: "/api" }));

		await waitFor(() => {
			expect(result.current.availability.isAvailabilityLoading).toBe(false);
		});

		expect(result.current.state.client).toEqual({
			name: "Ada",
			phone: "206-555-0101",
			email: "ada@example.com",
		});
		expect(result.current.availability.slots).toBeNull();

		act(() => {
			result.current.actions.open({
				id: "svc-1",
				title: "Custom Facial",
				duration: 60,
			});
		});

		expect(result.current.state.step).toBe(STEP.DATE);
		expect(result.current.state.isOpen).toBe(true);
		expect(result.current.availability.slots).toEqual({
			"2026-03-20": ["10:00 AM", "10:15 AM", "10:30 AM"],
		});
	});

	it("submits a completed booking and transitions to confirmed", async () => {
		global.fetch = jest
			.fn()
			.mockImplementationOnce(() =>
				mockJsonResponse({
					"2026-03-20": [["10:00", "11:30"]],
				}),
			)
			.mockImplementationOnce(() =>
				mockJsonResponse({
					pubUrl: "https://example.com/appointment/123",
				}),
			);

		const { result } = renderHook(() => useBookingWizard({ apiUrl: "/api" }));

		await waitFor(() => {
			expect(result.current.availability.isAvailabilityLoading).toBe(false);
		});

		act(() => {
			result.current.actions.open({
				id: "svc-1",
				title: "Custom Facial",
				duration: 60,
			});
			result.current.actions.selectDate("2026-03-20");
			result.current.actions.selectTime("10:00 AM");
			result.current.actions.saveClient({
				name: "Ada",
				phone: "206-555-0101",
				email: "ada@example.com",
			});
		});

		await act(async () => {
			await result.current.actions.confirm();
		});

		await waitFor(() => {
			expect(result.current.state.step).toBe(STEP.CONFIRMED);
		});

		expect(global.fetch).toHaveBeenNthCalledWith(
			2,
			"/api/appointments",
			expect.objectContaining({
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					serviceId: "svc-1",
					date: "2026-03-20",
					time: "10:00 AM",
					clientName: "Ada",
					clientPhone: "206-555-0101",
					clientEmail: "ada@example.com",
					payment: null,
				}),
			}),
		);
		expect(result.current.state.pubUrl).toBe(
			"https://example.com/appointment/123",
		);
	});

	it("stores submit errors without leaving the review step", async () => {
		global.fetch = jest
			.fn()
			.mockImplementationOnce(() =>
				mockJsonResponse({
					"2026-03-20": [["10:00", "11:30"]],
				}),
			)
			.mockImplementationOnce(() =>
				mockJsonResponse({ error: "Time slot unavailable" }, false, 409),
			);

		const { result } = renderHook(() => useBookingWizard({ apiUrl: "/api" }));

		await waitFor(() => {
			expect(result.current.availability.isAvailabilityLoading).toBe(false);
		});

		act(() => {
			result.current.actions.open({
				id: "svc-1",
				title: "Custom Facial",
				duration: 60,
			});
			result.current.actions.selectDate("2026-03-20");
			result.current.actions.selectTime("10:00 AM");
			result.current.actions.saveClient({
				name: "Ada",
				phone: "206-555-0101",
				email: "ada@example.com",
			});
		});

		await act(async () => {
			await result.current.actions.confirm();
		});

		await waitFor(() => {
			expect(result.current.state.submitError).toBe("Time slot unavailable");
		});

		expect(result.current.state.step).toBe(STEP.REVIEW);
	});

	it("handles empty service selection, back navigation, and close resets", async () => {
		global.fetch = jest.fn(() =>
			mockJsonResponse({
				"2026-03-20": [["10:00", "11:30"]],
			}),
		);

		const { result } = renderHook(() => useBookingWizard({ apiUrl: "/api" }));

		await waitFor(() => {
			expect(result.current.availability.isAvailabilityLoading).toBe(false);
		});

		act(() => {
			result.current.actions.open(null);
		});

		expect(result.current.state.isOpen).toBe(true);
		expect(result.current.state.step).toBe(STEP.SERVICE);
		expect(result.current.state.service).toBeNull();

		act(() => {
			result.current.actions.open({
				id: "svc-1",
				title: "Custom Facial",
				duration: 60,
			});
			result.current.actions.selectDate("2026-03-20");
		});

		expect(result.current.state.step).toBe(STEP.TIME);

		act(() => {
			result.current.actions.back();
		});

		expect(result.current.state.step).toBe(STEP.DATE);
		expect(result.current.state.selectedTime).toBeNull();

		act(() => {
			result.current.actions.selectTime("10:00 AM");
			result.current.actions.back();
		});

		expect(result.current.state.step).toBe(STEP.TIME);

		act(() => {
			result.current.actions.saveClient({
				name: "Ada",
				phone: "206-555-0101",
				email: "ada@example.com",
			});
			result.current.actions.back();
		});

		expect(result.current.state.step).toBe(STEP.CLIENT);

		act(() => {
			result.current.actions.close();
		});

		expect(result.current.state.isOpen).toBe(false);
		expect(result.current.state.step).toBe(STEP.SERVICE);
		expect(result.current.state.service).toBeNull();
		expect(result.current.state.selectedDate).toBeNull();
		expect(result.current.state.selectedTime).toBeNull();
		expect(result.current.state.pubUrl).toBeNull();
	});

	it("surfaces availability failures and ignores incomplete confirmations", async () => {
		global.fetch = jest.fn(() => Promise.reject(new Error("Network down")));

		const { result } = renderHook(() => useBookingWizard({ apiUrl: "/api" }));

		await waitFor(() => {
			expect(result.current.availability.isAvailabilityLoading).toBe(false);
		});

		expect(result.current.availability.availabilityError).toBe("Network down");
		expect(result.current.availability.slots).toBeNull();

		await act(async () => {
			await result.current.actions.confirm();
		});

		expect(global.fetch).toHaveBeenCalledTimes(1);
		expect(result.current.state.submitError).toBe("");
	});

	it("falls back to a generic submit error when booking creation throws", async () => {
		global.fetch = jest
			.fn()
			.mockImplementationOnce(() =>
				mockJsonResponse({
					"2026-03-20": [["10:00", "11:30"]],
				}),
			)
			.mockImplementationOnce(() =>
				Promise.reject(new Error("Request failed")),
			);

		const { result } = renderHook(() => useBookingWizard({ apiUrl: "/api" }));

		await waitFor(() => {
			expect(result.current.availability.isAvailabilityLoading).toBe(false);
		});

		act(() => {
			result.current.actions.open({
				id: "svc-1",
				title: "Custom Facial",
				duration: 60,
			});
			result.current.actions.selectDate("2026-03-20");
			result.current.actions.selectTime("10:00 AM");
			result.current.actions.saveClient({
				name: "Ada",
				phone: "206-555-0101",
				email: "ada@example.com",
			});
		});

		await act(async () => {
			await result.current.actions.confirm();
		});

		expect(result.current.state.step).toBe(STEP.REVIEW);
		expect(result.current.state.submitError).toBe(
			"Failed to create appointment",
		);
	});
});

describe("getServiceFromElement", () => {
	it("reads booking metadata from a DOM element dataset", () => {
		const button = document.createElement("button");
		button.dataset.serviceId = "svc-7";
		button.dataset.serviceTitle = "Hydrating Facial";
		button.dataset.duration = "75";

		expect(getServiceFromElement(button)).toEqual({
			id: "svc-7",
			title: "Hydrating Facial",
			duration: 75,
		});
	});

	it("returns null when no service id is present", () => {
		const button = document.createElement("button");

		expect(getServiceFromElement(button)).toBeNull();
	});
});
