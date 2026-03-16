import { addDays, formatDateForApi, formatDisplayDate } from "./dateUtils.js";

describe("bookingWizard/dateUtils", () => {
	it("adds days without mutating the original date", () => {
		const original = new Date("2026-03-15T12:00:00Z");

		const shifted = addDays(original, 2);

		expect(formatDateForApi(original)).toBe("2026-03-15");
		expect(formatDateForApi(shifted)).toBe("2026-03-17");
	});

	it("formats ISO dates for display and handles empty values", () => {
		expect(formatDisplayDate("2026-03-16")).toBe("Monday, March 16");
		expect(formatDisplayDate("")).toBe("");
	});
});
