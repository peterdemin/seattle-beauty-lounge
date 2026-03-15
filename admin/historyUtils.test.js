import assert from "node:assert/strict";
import {
	formatTime,
	groupDatesByDate,
	groupDatesByMonth,
	groupDatesByYear,
} from "./historyUtils.js";

try {
	const april2026 = new Date(2026, 3, 1);
	const april12 = new Date(2026, 3, 12);
	const april13 = new Date(2026, 3, 13);
	const may2026 = new Date(2026, 4, 1);
	const march2027 = new Date(2027, 2, 2);

	const yearGroups = groupDatesByYear([
		[april12, "e"],
		[april2026, "a"],
		[april13, "d"],
		[may2026, "b"],
		[march2027, "c"],
	]);
	assert.deepEqual(yearGroups, [
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

	const monthGroups = groupDatesByMonth([
		[april13, "a"],
		[april12, "b"],
		[may2026, "c"],
	]);
	assert.deepEqual(monthGroups, [
		[
			"April",
			[
				[april13, "a"],
				[april12, "b"],
			],
		],
		["May", [[may2026, "c"]]],
	]);

	const dateGroups = groupDatesByDate([
		[april12, "x"],
		[april12, "z"],
		[april13, "y"],
	]);
	assert.deepEqual(dateGroups, [
		[
			12,
			[
				[april12, "x"],
				[april12, "z"],
			],
		],
		[13, [[april13, "y"]]],
	]);

	assert.equal(formatTime("09:05"), "9:05 AM");
	assert.equal(formatTime("13:30"), "1:30 PM");

	console.log("historyUtils tests passed ✅");
} catch (error) {
	console.error("historyUtils tests failed ❌:", error.message);
	process.exit(1);
}
