import * as Sentry from "@sentry/react";

let sentryInitialized = false;

export function initBookingSentry(sentryDsn) {
	if (!sentryDsn || sentryInitialized) {
		return;
	}

	Sentry.init({
		dsn: sentryDsn,
		integrations: [
			Sentry.browserTracingIntegration(),
			Sentry.replayIntegration(),
		],
		tracesSampleRate: 1.0,
		tracePropagationTargets: [
			"http://127.0.0.1:8000/index.html",
			"https://staging.seattle-beauty-lounge.com/",
		],
		replaysSessionSampleRate: 0.1,
		replaysOnErrorSampleRate: 1.0,
		debug: true,
	});
	sentryInitialized = true;
}
