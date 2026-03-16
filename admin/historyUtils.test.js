import {
	formatTime,
	groupDatesByDate,
	groupDatesByMonth,
	groupDatesByYear,
} from "./historyUtils.js";

describe("historyUtils", () => {
	it("groups dates and formats time", () => {
		const april2026 = new Date(2026, 3, 1);
		const april12 = new Date(2026, 3, 12);
		const april13 = new Date(2026, 3, 13);
		const may2026 = new Date(2026, 4, 1);
		const march2027 = new Date(2027, 2, 2);

		expect(
			groupDatesByYear([
				[april12, "e"],
				[april2026, "a"],
				[april13, "d"],
				[may2026, "b"],
				[march2027, "c"],
			]),
		).toEqual([
			[
				2026,
				[
					[april12, "e"],
					[april2026, "a"],
					[april13, "d"],
					[may2026, "b"],
				],
			],
			[2027, [[march2027, "c"]]],
		]);

		expect(
			groupDatesByMonth([
				[april13, "a"],
				[april12, "b"],
				[may2026, "c"],
			]),
		).toEqual([
			[
				"April",
				[
					[april13, "a"],
					[april12, "b"],
				],
			],
			["May", [[may2026, "c"]]],
		]);

		expect(
			groupDatesByDate([
				[april12, "x"],
				[april12, "z"],
				[april13, "y"],
			]),
		).toEqual([
			[
				12,
				[
					[april12, "x"],
					[april12, "z"],
				],
			],
			[13, [[april13, "y"]]],
		]);

		expect(formatTime("09:05")).toBe("9:05 AM");
		expect(formatTime("13:30")).toBe("1:30 PM");
	});
});
