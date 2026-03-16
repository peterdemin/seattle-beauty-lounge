import React, { useMemo, useState } from "react";
import { DayPicker } from "react-day-picker";

import NextButton from "../NextButton.jsx";
import { addDays, formatDateForApi } from "../dateUtils.js";

function PickDateStep({ slots, isLoading, error, onDateSelect }) {
	const [selectedDay, setSelectedDay] = useState(null);
	const disabledDates = useMemo(() => {
		if (!slots) {
			return [];
		}
		const dates = [];
		for (const dateStr in slots) {
			if (slots[dateStr].length === 0) {
				const [year, month, day] = dateStr.split("-").map(Number);
				dates.push(new Date(year, month - 1, day));
			}
		}
		return dates;
	}, [slots]);

	const today = new Date();
	const firstDay = addDays(today, 1);
	const lastDay = addDays(today, 7 * 6);

	if (isLoading) {
		return <p className="text-center text-primary">Loading availability...</p>;
	}

	if (error) {
		return <p className="text-center text-red-600">{error}</p>;
	}

	if (!slots) {
		return (
			<p className="text-center text-primary">Select a service to continue.</p>
		);
	}

	return (
		<div>
			<h2 className="text-2xl text-center font-light text-primary">
				Pick a Date
			</h2>
			<DayPicker
				mode="single"
				selected={selectedDay}
				onSelect={setSelectedDay}
				modifiers={{
					disabled: [
						{ before: firstDay },
						{ after: lastDay },
						...disabledDates,
					],
				}}
			/>
			<NextButton
				handleNext={() => {
					if (selectedDay) {
						onDateSelect(formatDateForApi(selectedDay));
					}
				}}
				disabled={!selectedDay}
			/>
		</div>
	);
}

export default PickDateStep;
