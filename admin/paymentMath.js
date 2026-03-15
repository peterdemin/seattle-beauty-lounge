export function calculateTipCents(subtotalCents, tipPercent) {
	return Math.round((subtotalCents * tipPercent) / 100);
}

export function calculateTotalCents(subtotalCents, tipPercent) {
	return subtotalCents + calculateTipCents(subtotalCents, tipPercent);
}

export function toDollars(cents) {
	return (Number(cents) / 100).toFixed(2);
}
