import assert from "node:assert/strict";
import { parseLocalDate, parseLocalDateTime } from "./dateUtils.js";

try {
	const date = parseLocalDate("2026-03-14");
	assert.equal(date.getFullYear(), 2026);
	assert.equal(date.getMonth(), 2);
	assert.equal(date.getDate(), 14);

	const dateTime = parseLocalDateTime("2026-03-14", "13:30");
	assert.equal(dateTime.getFullYear(), 2026);
	assert.equal(dateTime.getMonth(), 2);
	assert.equal(dateTime.getDate(), 14);
	assert.equal(dateTime.getHours(), 13);
	assert.equal(dateTime.getMinutes(), 30);

	console.log("dateUtils tests passed ✅");
} catch (error) {
	console.error("dateUtils tests failed ❌:", error.message);
	process.exit(1);
}
