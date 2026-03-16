export function addDays(date, days) {
	const result = new Date(date);
	result.setDate(result.getDate() + days);
	return result;
}

export function formatDateForApi(date) {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, "0");
	const day = String(date.getDate()).padStart(2, "0");
	return `${year}-${month}-${day}`;
}

export function formatDisplayDate(isoDate) {
	if (!isoDate) {
		return "";
	}
	const [yearValue, monthValue, dayValue] = isoDate.split("-").map(Number);
	const date = new Date(yearValue, monthValue - 1, dayValue);
	const dayOfWeek = date.toLocaleString("en-US", { weekday: "long" });
	const monthName = date.toLocaleString("en-US", { month: "long" });
	const dayOfMonth = date.getDate();
	return `${dayOfWeek}, ${monthName} ${dayOfMonth}`;
}
