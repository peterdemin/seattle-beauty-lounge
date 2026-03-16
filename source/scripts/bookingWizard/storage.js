const STORAGE_KEYS = {
	name: "clientName",
	phone: "clientPhone",
	email: "clientEmail",
};

export function getStoredClient() {
	return {
		name: localStorage.getItem(STORAGE_KEYS.name) || "",
		phone: localStorage.getItem(STORAGE_KEYS.phone) || "",
		email: localStorage.getItem(STORAGE_KEYS.email) || "",
	};
}

export function saveStoredClient(client) {
	localStorage.setItem(STORAGE_KEYS.name, client.name);
	localStorage.setItem(STORAGE_KEYS.phone, client.phone);
	localStorage.setItem(STORAGE_KEYS.email, client.email);
}
