import { useEffect, useMemo, useReducer } from "react";

import { getAvailableSlots } from "../availability.js";
import { STEP } from "./constants.js";
import { getStoredClient, saveStoredClient } from "./storage.js";

function getInitialState() {
	return {
		isOpen: false,
		step: STEP.SERVICE,
		service: null,
		selectedDate: null,
		selectedTime: null,
		client: getStoredClient(),
		pubUrl: null,
		submitError: "",
	};
}

function bookingReducer(state, action) {
	switch (action.type) {
		case "open":
			return {
				...state,
				isOpen: true,
				step: action.service ? STEP.DATE : STEP.SERVICE,
				service: action.service,
				selectedDate: null,
				selectedTime: null,
				pubUrl: null,
				submitError: "",
			};
		case "close":
			return {
				...state,
				isOpen: false,
				step: STEP.SERVICE,
				service: null,
				selectedDate: null,
				selectedTime: null,
				pubUrl: null,
				submitError: "",
			};
		case "back":
			if (state.step === STEP.DATE || state.step === STEP.SERVICE) {
				return {
					...state,
					step: STEP.SERVICE,
					service: null,
					selectedDate: null,
					selectedTime: null,
					submitError: "",
				};
			}
			if (state.step === STEP.TIME) {
				return {
					...state,
					step: STEP.DATE,
					selectedTime: null,
					submitError: "",
				};
			}
			if (state.step === STEP.CLIENT) {
				return { ...state, step: STEP.TIME, submitError: "" };
			}
			if (state.step === STEP.REVIEW) {
				return { ...state, step: STEP.CLIENT, submitError: "" };
			}
			return state;
		case "select_date":
			return {
				...state,
				selectedDate: action.date,
				selectedTime: null,
				step: STEP.TIME,
				submitError: "",
			};
		case "select_time":
			return {
				...state,
				selectedTime: action.time,
				step: STEP.CLIENT,
				submitError: "",
			};
		case "save_client":
			return {
				...state,
				client: action.client,
				step: STEP.REVIEW,
				submitError: "",
			};
		case "submit_success":
			return {
				...state,
				pubUrl: action.pubUrl,
				step: STEP.CONFIRMED,
				submitError: "",
			};
		case "submit_error":
			return {
				...state,
				submitError: action.error,
			};
		default:
			return state;
	}
}

function availabilityReducer(state, action) {
	switch (action.type) {
		case "loading":
			return { ...state, isLoading: true, error: "" };
		case "success":
			return {
				availability: action.availability,
				isLoading: false,
				error: "",
			};
		case "error":
			return {
				availability: null,
				isLoading: false,
				error: action.error,
			};
		default:
			return state;
	}
}

function useAvailability(apiUrl, duration) {
	const [availability, dispatch] = useReducer(availabilityReducer, {
		availability: null,
		isLoading: true,
		error: "",
	});

	useEffect(() => {
		let cancelled = false;

		async function loadAvailability() {
			dispatch({ type: "loading" });
			try {
				const response = await fetch(`${apiUrl}/availability`);
				if (!response.ok) {
					throw new Error(`Failed to load availability (${response.status})`);
				}
				const data = await response.json();
				if (!cancelled) {
					dispatch({ type: "success", availability: data });
				}
			} catch (error) {
				if (!cancelled) {
					dispatch({
						type: "error",
						error:
							error instanceof Error
								? error.message
								: "Failed to load availability",
					});
				}
			}
		}

		loadAvailability();
		return () => {
			cancelled = true;
		};
	}, [apiUrl]);

	const slots = useMemo(() => {
		if (!duration || !availability.availability) {
			return null;
		}
		return getAvailableSlots(availability.availability, duration);
	}, [availability.availability, duration]);

	return {
		availabilityError: availability.error,
		isAvailabilityLoading: availability.isLoading,
		slots,
	};
}

async function submitAppointment({ apiUrl, serviceId, date, time, client }) {
	try {
		const response = await fetch(`${apiUrl}/appointments`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				serviceId,
				date,
				time,
				clientName: client.name,
				clientPhone: client.phone,
				clientEmail: client.email,
				payment: null,
			}),
		});
		const payload = await response.json();
		if (response.ok) {
			return { pubUrl: payload.pubUrl };
		}
		return { error: payload.error || "Failed to create appointment" };
	} catch (_error) {
		return { error: "Failed to create appointment" };
	}
}

export function getServiceFromElement(element) {
	const serviceId = element.dataset.serviceId || null;
	if (!serviceId) {
		return null;
	}
	return {
		id: serviceId,
		title: element.dataset.serviceTitle || "",
		duration: Number(element.dataset.duration),
	};
}

export function useBookingWizard({ apiUrl }) {
	const [state, dispatch] = useReducer(
		bookingReducer,
		undefined,
		getInitialState,
	);
	const availability = useAvailability(apiUrl, state.service?.duration ?? null);

	const actions = {
		open(service) {
			dispatch({ type: "open", service });
		},
		close() {
			dispatch({ type: "close" });
		},
		back() {
			dispatch({ type: "back" });
		},
		selectDate(date) {
			dispatch({ type: "select_date", date });
		},
		selectTime(time) {
			dispatch({ type: "select_time", time });
		},
		saveClient(client) {
			saveStoredClient(client);
			dispatch({ type: "save_client", client });
		},
		async confirm() {
			if (!state.service || !state.selectedDate || !state.selectedTime) {
				return;
			}
			const result = await submitAppointment({
				apiUrl,
				serviceId: state.service.id,
				date: state.selectedDate,
				time: state.selectedTime,
				client: state.client,
			});
			if (result.pubUrl) {
				dispatch({ type: "submit_success", pubUrl: result.pubUrl });
				return;
			}
			dispatch({ type: "submit_error", error: result.error });
		},
	};

	return {
		state,
		availability,
		actions,
	};
}
