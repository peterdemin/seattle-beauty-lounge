import { parseLocalDate, parseLocalDateTime } from "./dateUtils.js";

describe("dateUtils", () => {
	it("parses local dates and datetimes", () => {
		const date = parseLocalDate("2026-03-14");
		expect(date.getFullYear()).toBe(2026);
		expect(date.getMonth()).toBe(2);
		expect(date.getDate()).toBe(14);

		const dateTime = parseLocalDateTime("2026-03-14", "13:30");
		expect(dateTime.getFullYear()).toBe(2026);
		expect(dateTime.getMonth()).toBe(2);
		expect(dateTime.getDate()).toBe(14);
		expect(dateTime.getHours()).toBe(13);
		expect(dateTime.getMinutes()).toBe(30);
	});
});
