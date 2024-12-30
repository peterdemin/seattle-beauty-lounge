const STEP = 15; // minutes

/**
 * timeString: "HH:MM" (e.g. "10:00")
 * returns integer minutes from midnight (e.g. 600)
 */
function parseTime(timeString) {
	const [hours, minutes] = timeString.split(":").map(Number);
	return hours * 60 + minutes;
}

/*
 * totalMinutes: number of minutes from midnight (0 - 1440)
 * returns "HH:MM" in 24-hour format
 */
function formatTime(totalMinutes) {
	const hours = Math.floor(totalMinutes / 60);
	const minutes = totalMinutes % 60;
	// Pad with leading zeros if needed (e.g. "09:05")
	return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

/**
 * range = ["HH:MM", "HH:MM"]  e.g. ["10:00", "17:00"]
 * serviceDuration = number of minutes (e.g. 180)
 * returns array of "HH:MM" times (e.g. ["10:00", "10:15", ... "14:00"])
 */
function getSlotsForRange(range, serviceDuration) {
	const [rangeStartStr, rangeEndStr] = range;
	const rangeStart = parseTime(rangeStartStr);
	const rangeEnd = parseTime(rangeEndStr);
	const slots = [];
	for (
		let start = rangeStart;
		start <= rangeEnd - serviceDuration;
		start += STEP
	) {
		slots.push(formatTime(start));
	}
	return slots;
}

/**
 * availability: {
 *   "YYYY-MM-DD": [
 *     ["startTime", "endTime"],   // e.g. ["10:00", "17:00"]
 *     ...
 *   ],
 *   ...
 * }
 * serviceDuration: integer minutes (e.g. 180)
 *
 * Returns an object with the same date keys, each an array of possible start times.
 */
function getAvailableSlots(availability, serviceDuration) {
	const slotsByDate = {};
	for (const date in availability) {
		const ranges = availability[date];
		slotsByDate[date] = [];
		for (const range of ranges) {
			const slots = getSlotsForRange(range, serviceDuration);
			slotsByDate[date] = slotsByDate[date].concat(slots);
		}
	}
	return slotsByDate;
}

export default getAvailableSlots;
