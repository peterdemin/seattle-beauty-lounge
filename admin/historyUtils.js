export function groupBy(dates, keyfunc) {
	const grouped = [];
	let curKey = null;
	for (const [date, item] of dates) {
		const key = keyfunc(date);
		if (key !== curKey) {
			grouped.push([key, []]);
			curKey = key;
		}
		grouped[grouped.length - 1][1].push([date, item]);
	}
	return grouped;
}

export function groupDatesByYear(dates) {
	return groupBy(dates, (date) => date.getFullYear());
}

export function groupDatesByMonth(dates) {
	return groupBy(dates, (date) =>
		new Intl.DateTimeFormat("en-US", { month: "long" }).format(date),
	);
}

export function groupDatesByDate(dates) {
	return groupBy(dates, (date) => date.getDate());
}

export function formatTime(timeStr) {
	const d = new Date();
	const [hours, minutes] = timeStr.split(":").map(Number);
	d.setHours(hours);
	d.setMinutes(minutes);
	const formatter = new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	});
	return formatter.format(d);
}
