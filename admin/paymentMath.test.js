import {
	calculateTipCents,
	calculateTotalCents,
	toDollars,
} from "./paymentMath.js";

describe("paymentMath", () => {
	it("calculates tips, totals, and dollar formatting", () => {
		expect(calculateTipCents(6500, 20)).toBe(1300);
		expect(calculateTipCents(3333, 15)).toBe(500);

		expect(calculateTotalCents(6500, 0)).toBe(6500);
		expect(calculateTotalCents(6500, 15)).toBe(7475);
		expect(calculateTotalCents(3333, 10)).toBe(3666);

		expect(toDollars(6500)).toBe("65.00");
		expect(toDollars(3333)).toBe("33.33");
	});
});
