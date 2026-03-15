export function parseLocalDate(dateStr) {
	const [year, month, day] = dateStr.split("-").map(Number);
	return new Date(year, month - 1, day);
}

export function parseLocalDateTime(dateStr, timeStr) {
	const [year, month, day] = dateStr.split("-").map(Number);
	const [hours, minutes] = timeStr.split(":").map(Number);
	return new Date(year, month - 1, day, hours, minutes);
}
