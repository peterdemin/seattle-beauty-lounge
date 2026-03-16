import renderConfirmation from "./ConfirmationTemplate.js";

describe("ConfirmationTemplate", () => {
	it("renders the booking confirmation content", () => {
		const clientName = "Ada";
		const clientEmail = "ada@example.com";
		const clientPhone = "206-555-0101";
		const pubUrl = "https://example.com/appointment/abc123";

		const html = renderConfirmation(
			clientName,
			clientEmail,
			clientPhone,
			pubUrl,
		);

		expect(html).toMatch(/Thank you, Ada!/);
		expect(html).toMatch(/Your appointment is confirmed\./);
		expect(html).toMatch(
			new RegExp(`email confirmation at ${clientEmail.replace(".", "\\.")}`),
		);
		expect(html).toMatch(
			new RegExp(
				`reminder the day before service to ${clientPhone.replace("-", "\\-")}`,
			),
		);
		expect(html).toMatch(
			new RegExp(`href="${pubUrl.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`),
		);
		expect(html).toMatch(/href="tel:\+13016588708"/);
	});
});
