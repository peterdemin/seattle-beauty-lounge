import { calculateTipCents, calculateTotalCents } from "./paymentMath.js";

export const tipOptions = [15, 20, 25, 0];

export function getTipLabel(percent) {
	if (percent === 0) {
		return "No tip";
	}
	return `${percent}%`;
}

export function buildPaymentSummary(subtotalCents, tipPercent) {
	const subtotal = Number(subtotalCents) || 0;
	const tipCents = calculateTipCents(subtotal, tipPercent);
	const totalCents = calculateTotalCents(subtotal, tipPercent);
	return { subtotal, tipCents, totalCents };
}
