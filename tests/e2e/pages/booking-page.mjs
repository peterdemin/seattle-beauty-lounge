import { expect } from "@playwright/test";

export class BookingPage {
	constructor(page) {
		this.page = page;
		this.root = page.locator("#book");
	}

	get serviceTable() {
		return this.page.locator("#service-table");
	}

	get datePickerCaption() {
		return this.page.locator(".rdp-caption_label").first();
	}

	get nextCalendarMonthButton() {
		return this.page.locator(".rdp-button_next");
	}

	get dayButtons() {
		return this.page.locator(
			".rdp-day_button:not([disabled]):not(.rdp-outside)",
		);
	}

	get nextStepButton() {
		return this.root.locator('button:has-text("Next")').first();
	}

	get confirmButton() {
		return this.page.locator('button:has-text("Confirm")').first();
	}

	async clearSessionState() {
		await this.page.addInitScript(() => {
			window.localStorage.clear();
		});
	}

	async open() {
		await this.page.goto("/");
	}

	async openServiceSelection() {
		await this.page.locator('.book-btn[type="button"]').first().click();
		await this.serviceTable.waitFor({ state: "visible", timeout: 10000 });
	}

	async selectFirstService() {
		const serviceRow = this.serviceTable.locator("tr.book-btn").first();
		await expect(serviceRow).toHaveCount(1);
		const serviceDuration = await serviceRow.getAttribute("data-duration");
		const serviceDurationMinutes = Number(serviceDuration);
		if (
			!Number.isFinite(serviceDurationMinutes) ||
			serviceDurationMinutes <= 0
		) {
			throw new Error(`Invalid service duration: ${serviceDuration}`);
		}
		await serviceRow.first().click();
		await expect(this.root.getByText("Pick a Date")).toBeVisible({
			timeout: 10000,
		});
		return serviceDurationMinutes;
	}

	async selectDate(isoDate) {
		const targetDate = new Date(`${isoDate}T00:00:00`);
		const targetDayText = String(targetDate.getDate());
		const targetMonthText = targetDate.toLocaleString("en-US", {
			month: "long",
		});
		const targetMonthShortText = targetDate.toLocaleString("en-US", {
			month: "short",
		});
		const targetYearText = String(targetDate.getFullYear());

		for (let i = 0; i < 24; i += 1) {
			const caption = (await this.datePickerCaption.textContent()) || "";
			const trimmedCaption = caption.trim();
			const captionMatch = /([A-Za-z]{3,})\s+(\d{4})/.exec(trimmedCaption);
			const captionMonth = captionMatch?.[1];
			const captionYear = captionMatch?.[2];
			if (
				captionMonth &&
				captionYear &&
				captionYear === targetYearText &&
				(captionMonth === targetMonthText ||
					captionMonth === targetMonthShortText)
			) {
				const dateButton = this.dayButtons.filter({
					hasText: new RegExp(`^${targetDayText}$`),
				});
				if ((await dateButton.count()) > 0) {
					await dateButton.first().click();
					return;
				}
			}
			await this.nextCalendarMonthButton.click();
		}
		throw new Error(`No available date found for day ${targetDayText}`);
	}

	async pickRandomTime() {
		const timeButtons = this.root.locator("button").filter({
			hasText: /^\s*\d{1,2}:\d{2}\s*(AM|PM)\s*$/,
		});
		const timeButtonCount = await timeButtons.count();
		expect(timeButtonCount).toBeGreaterThan(0);
		const randomTimeIndex = Math.floor(Math.random() * timeButtonCount);
		await timeButtons.nth(randomTimeIndex).click();
	}

	async fillCustomerInfo(customer) {
		await this.page.getByLabel("FULL NAME").fill(customer.name);
		await this.page.getByLabel("PHONE NUMBER").fill(customer.phone);
		await this.page.getByLabel("E-MAIL").fill(customer.email);
		await this.page.locator("#consent").check();
	}

	async proceedToNextStep() {
		await this.nextStepButton.click();
	}

	async goToStepText(stepName) {
		await expect(this.root.getByText(stepName)).toBeVisible({ timeout: 10000 });
	}

	async confirmBooking() {
		await this.confirmButton.click();
	}

	async assertAppointmentConfirmed(name) {
		await expect(this.page.getByText(`Thank you, ${name}!`)).toBeVisible();
		await expect(
			this.page.getByText("Your appointment is confirmed."),
		).toBeVisible();
	}
}
