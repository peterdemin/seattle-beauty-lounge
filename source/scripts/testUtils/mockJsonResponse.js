export function mockJsonResponse(body, ok = true, status = 200) {
	return Promise.resolve({
		ok,
		status,
		json: () => Promise.resolve(body),
		text: () => Promise.resolve(String(body)),
	});
}
