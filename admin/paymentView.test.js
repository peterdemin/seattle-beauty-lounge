import assert from "node:assert/strict";
import { buildPaymentSummary, getTipLabel } from "./paymentView.js";

try {
	assert.equal(getTipLabel(0), "No tip");
	assert.equal(getTipLabel(15), "15%");
	assert.equal(getTipLabel(25), "25%");

	assert.deepEqual(buildPaymentSummary(6500, 0), {
		subtotal: 6500,
		tipCents: 0,
		totalCents: 6500,
	});
	assert.deepEqual(buildPaymentSummary(6500, 20), {
		subtotal: 6500,
		tipCents: 1300,
		totalCents: 7800,
	});
	assert.deepEqual(buildPaymentSummary(3333, 15), {
		subtotal: 3333,
		tipCents: 500,
		totalCents: 3833,
	});

	console.log("paymentView tests passed ✅");
} catch (error) {
	console.error("paymentView tests failed ❌:", error.message);
	process.exit(1);
}
