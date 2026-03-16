import { buildPaymentSummary, getTipLabel } from "./paymentView.js";

describe("paymentView", () => {
	it("formats tip labels and payment summaries", () => {
		expect(getTipLabel(0)).toBe("No tip");
		expect(getTipLabel(15)).toBe("15%");
		expect(getTipLabel(25)).toBe("25%");

		expect(buildPaymentSummary(6500, 0)).toEqual({
			subtotal: 6500,
			tipCents: 0,
			totalCents: 6500,
		});
		expect(buildPaymentSummary(6500, 20)).toEqual({
			subtotal: 6500,
			tipCents: 1300,
			totalCents: 7800,
		});
		expect(buildPaymentSummary(3333, 15)).toEqual({
			subtotal: 3333,
			tipCents: 500,
			totalCents: 3833,
		});
	});
});
