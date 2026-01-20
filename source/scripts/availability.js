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
	let hours = Math.floor(totalMinutes / 60);
	const minutes = totalMinutes % 60;
	let ampm = "AM";
	if (hours >= 12) {
		ampm = "PM";
		if (hours > 12) {
			hours -= 12;
		}
	}
	// Pad minutes with leading zeros if needed (e.g. "9:05")
	return `${String(hours)}:${String(minutes).padStart(2, "0")} ${ampm}`;
}

/**
 * minutes = number of minutes (e.g. 185)
 * returns minutes rounded up so it's divisible by STEP
 */
function roundUp(minutes) {
	if (minutes % STEP === 0) {
		return minutes;
	}
	return (Math.floor(minutes / STEP) + 1) * STEP;
}

/**
 * range = ["hh:MM", "hh:MM"]  e.g. ["9:00", "17:00"]
 * serviceDuration = number of minutes (e.g. 180)
 * returns array of "HH:MM" times (e.g. ["10:00", "10:15", ... "14:00"])
 */
function getSlotsForRange(range, serviceDuration) {
	const [rangeStartStr, rangeEndStr] = range;
	const rangeStart = roundUp(parseTime(rangeStartStr));
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
export function getAvailableSlots(availability, serviceDuration) {
	const slotsByDate = {};
	for (const date in availability) {
		slotsByDate[date] = [];
		for (const range of availability[date]) {
			slotsByDate[date] = slotsByDate[date].concat(
				getSlotsForRange(range, serviceDuration),
			);
		}
	}
	return slotsByDate;
}

export function skipCount(timeStr, idx) {
	const targetPos = idx % 4;
	const minutes = timeStr.split(" ")[0].split(":")[1];
	const currentPos = { "00": 0, 15: 1, 30: 2, 45: 3 }[minutes];
	let delta = currentPos - targetPos;
	if (delta < 0) {
		delta += 4;
	}
	return delta;
}

export function insertSkips(times) {
	let idx = 0;
	const res = [];
	for (const time of times) {
		const skips = skipCount(time, idx);
		for (let i = 0; i < skips; i += 1) {
			res.push(null);
		}
		res.push(time);
		idx += skips + 1;
	}
	return res;
}
