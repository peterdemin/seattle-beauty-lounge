const SLOT_STEP_MINUTES = 15;

export function formatMinutesToTime(totalMinutes) {
	const hours24 = Math.floor(totalMinutes / 60);
	const minutes = String(totalMinutes % 60).padStart(2, "0");
	let hours12 = hours24 % 12;
	if (hours12 === 0) {
		hours12 = 12;
	}
	const suffix = hours24 >= 12 ? "PM" : "AM";
	return `${hours12}:${minutes} ${suffix}`;
}

function getSlotsForRange(range, durationMinutes) {
	const [startTime, endTime] = range;
	if (!startTime || !endTime) {
		return [];
	}
	const [startHours, startMinutes] = startTime.split(":").map(Number);
	const [endHours, endMinutes] = endTime.split(":").map(Number);
	let start = startHours * 60 + startMinutes;
	const end = endHours * 60 + endMinutes;
	const modulo = start % SLOT_STEP_MINUTES;
	if (modulo !== 0) {
		start += SLOT_STEP_MINUTES - modulo;
	}
	const slots = [];
	for (
		let minute = start;
		minute <= end - durationMinutes;
		minute += SLOT_STEP_MINUTES
	) {
		slots.push(formatMinutesToTime(minute));
	}
	return slots;
}

function nextMidnightPlus(days, baseDate = new Date()) {
	const minDate = new Date(baseDate);
	minDate.setHours(0, 0, 0, 0);
	minDate.setDate(minDate.getDate() + days);
	return minDate;
}

export function buildAvailableSlotsByDate(availabilityData, durationMinutes) {
	const minDate = nextMidnightPlus(1);
	return Object.entries(availabilityData).reduce((acc, [date, ranges]) => {
		const dateValue = new Date(`${date}T00:00:00`);
		if (Number.isNaN(dateValue.getTime()) || dateValue < minDate) {
			return acc;
		}
		if (!Array.isArray(ranges)) {
			return acc;
		}
		let dateSlots = [];
		for (const range of ranges) {
			if (Array.isArray(range) && range.length === 2) {
				dateSlots = dateSlots.concat(getSlotsForRange(range, durationMinutes));
			}
		}
		if (dateSlots.length > 0) {
			acc[date] = dateSlots;
		}
		return acc;
	}, {});
}

export function pickRandomSlot(availabilityByDate) {
	const availableSlots = Object.entries(availabilityByDate).flatMap(
		([date, timeslots]) => timeslots.map((time) => ({ date, time })),
	);
	if (availableSlots.length === 0) {
		throw new Error("No available appointment slots found.");
	}
	return availableSlots[Math.floor(Math.random() * availableSlots.length)];
}

export function assertHasAvailability(availabilityByDate) {
	const dates = Object.entries(availabilityByDate)
		.filter(([, slots]) => slots.length > 0)
		.map(([date]) => date)
		.sort();
	return dates;
}
