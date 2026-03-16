import { getAvailableSlots, insertSkips, skipCount } from "./availability.js";

describe("availability", () => {
	it("builds available slots from time ranges", () => {
		expect(
			getAvailableSlots({ "2014-04-14": [["10:00", "12:00"]] }, 90),
		).toEqual({ "2014-04-14": ["10:00 AM", "10:15 AM", "10:30 AM"] });
		expect(
			getAvailableSlots({ "2014-04-14": [["10:07", "12:00"]] }, 90),
		).toEqual({ "2014-04-14": ["10:15 AM", "10:30 AM"] });
		expect(
			getAvailableSlots({ "2014-04-14": [["14:14", "15:15"]] }, 60),
		).toEqual({ "2014-04-14": ["2:15 PM"] });
		expect(
			getAvailableSlots({ "2014-04-14": [["12:00", "13:00"]] }, 60),
		).toEqual({ "2014-04-14": ["12:00 PM"] });
	});

	it("computes slot alignment skips", () => {
		expect(skipCount("12:00 AM", 0)).toBe(0);
		expect(skipCount("12:15 AM", 1)).toBe(0);
		expect(skipCount("12:15 AM", 0)).toBe(1);
		expect(skipCount("12:30 PM", 0)).toBe(2);
		expect(skipCount("12:45 PM", 0)).toBe(3);
	});

	it("inserts placeholder cells for skipped grid positions", () => {
		expect(insertSkips(["10:00 AM", "10:15 AM"])).toEqual([
			"10:00 AM",
			"10:15 AM",
		]);
		expect(insertSkips(["10:00 AM", "10:30 AM"])).toEqual([
			"10:00 AM",
			null,
			"10:30 AM",
		]);
		expect(insertSkips(["10:45 AM"])).toEqual([null, null, null, "10:45 AM"]);
		expect(insertSkips(["10:00 AM", "11:00 AM"])).toEqual([
			"10:00 AM",
			null,
			null,
			null,
			"11:00 AM",
		]);
	});
});
