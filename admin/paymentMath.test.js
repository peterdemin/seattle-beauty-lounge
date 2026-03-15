import assert from "node:assert/strict";
import {
	calculateTipCents,
	calculateTotalCents,
	toDollars,
} from "./paymentMath.js";

try {
	assert.equal(calculateTipCents(6500, 20), 1300);
	assert.equal(calculateTipCents(3333, 15), 500);

	assert.equal(calculateTotalCents(6500, 0), 6500);
	assert.equal(calculateTotalCents(6500, 15), 7475);
	assert.equal(calculateTotalCents(3333, 10), 3666);

	assert.equal(toDollars(6500), "65.00");
	assert.equal(toDollars(3333), "33.33");

	console.log("paymentMath tests passed ✅");
} catch (error) {
	console.error("paymentMath tests failed ❌:", error.message);
	process.exit(1);
}
