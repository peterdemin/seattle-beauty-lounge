import assert from "node:assert/strict";
import { getAvailableSlots, insertSkips, skipCount } from "./availability.js";

try {
	assert.deepEqual(
		getAvailableSlots({ "2014-04-14": [["10:00", "12:00"]] }, 90),
		{ "2014-04-14": ["10:00 AM", "10:15 AM", "10:30 AM"] },
	);
	assert.deepEqual(
		getAvailableSlots({ "2014-04-14": [["10:07", "12:00"]] }, 90),
		{ "2014-04-14": ["10:15 AM", "10:30 AM"] },
	);
	assert.deepEqual(
		getAvailableSlots({ "2014-04-14": [["14:14", "15:15"]] }, 60),
		{ "2014-04-14": ["2:15 PM"] },
	);
	assert.deepEqual(
		getAvailableSlots({ "2014-04-14": [["12:00", "13:00"]] }, 60),
		{ "2014-04-14": ["12:00 PM"] },
	);

	assert.equal(skipCount("12:00 AM", 0), 0);
	assert.equal(skipCount("12:15 AM", 1), 0);
	assert.equal(skipCount("12:15 AM", 0), 1);
	assert.equal(skipCount("12:30 PM", 0), 2);
	assert.equal(skipCount("12:45 PM", 0), 3);

	assert.deepEqual(insertSkips(["10:00 AM", "10:15 AM"]), [
		"10:00 AM",
		"10:15 AM",
	]);
	assert.deepEqual(insertSkips(["10:00 AM", "10:30 AM"]), [
		"10:00 AM",
		null,
		"10:30 AM",
	]);
	assert.deepEqual(insertSkips(["10:45 AM"]), [null, null, null, "10:45 AM"]);
	assert.deepEqual(insertSkips(["10:00 AM", "11:00 AM"]), [
		"10:00 AM",
		null,
		null,
		null,
		"11:00 AM",
	]);
	console.log("All tests passed ✅");
} catch (error) {
	console.error("Test failed ❌:", error.message);
	process.exit(1);
}
