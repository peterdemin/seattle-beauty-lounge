import * as Square from "@square/web-sdk";
import { useEffect, useRef, useState } from "react";

function SquarePayment({
	applicationId,
	locationId,
	apiUrl,
	active,
	onPayment,
}) {
	const [payments, setPayments] = useState(null);
	const idempotencyKey = useRef(null);
	const [message, setMessage] = useState("");

	if (idempotencyKey.current === null) {
		const characters =
			"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		const charactersLength = characters.length;
		let result = "";
		for (let i = 0; i < 8; i++) {
			result += characters.charAt(Math.floor(Math.random() * charactersLength));
		}
		idempotencyKey.current = result;
	}

	useEffect(() => {
		if (!applicationId || !locationId) {
			return;
		}
		Square.payments(applicationId, locationId).then((res) => {
			setPayments(res);
		});
	}, [applicationId, locationId]);

	const onTokenize = (token) => {
		setMessage("");
		fetch(`${apiUrl}/square/pay`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				idempotencyKey: idempotencyKey.current,
				token,
			}),
		})
			.then((res) => {
				if (res.ok) {
					return res.json();
				}
				console.error(res);
				setMessage("Failed to book an appointment. Please try again later.");
			})
			.then((json) => {
				if (json.payment) {
					onPayment(token);
					return;
				}
				console.error(json);
				if (json.error) {
					setMessage(`ERROR: ${json.error}`);
					return;
				}
				setMessage(`ERROR: ${JSON.stringify(json)}`);
			})
			.catch((error) => {
				console.error(error);
				setMessage(
					"Booking failed because network server is unreachable. Please check your network connection and try again.",
				);
			});
	};

	return (
		<div className={active ? "" : "hidden"}>
			<CreditCard payments={payments} callback={onTokenize} />
			<div className={message ? "text-red-400 font-medium" : "invisible"}>
				{message}
			</div>
		</div>
	);
}

function CreditCard({ payments, callback }) {
	const [card, setCard] = useState(null);
	const [isSubmitting, setIsSubmitting] = useState(false);
	const cardRef = useRef(null);
	const [message, setMessage] = useState("");

	const handleClick = (e) => {
		e.stopPropagation();
		if (!card) {
			return;
		}
		setIsSubmitting(true);
		setMessage("");
		card
			.tokenize()
			.then((result) => {
				if (result.status === "OK") {
					callback(result.token);
				} else {
					let message = `Payment failed with status: ${result.status}.`;
					if (result.errors) {
						message += ` Error: ${result.errors[0].message}`;
					}
					setMessage(message);
				}
				setIsSubmitting(false);
			})
			.catch(() => {
				setMessage(
					"Booking failed because network server is unreachable. Please check your network connection and try again.",
				);
				setIsSubmitting(false);
			});
	};

	useEffect(() => {
		if (!payments) {
			return;
		}
		let cardObj = null;
		payments.card({}).then((res) => {
			cardObj = res;
			cardObj.attach(cardRef.current).then(() => {
				setCard(cardObj);
			});
		});
		return () => {
			if (!cardObj) {
				return;
			}
			cardObj.destroy();
			setCard(null);
		};
	}, [payments]);

	const disabled = !card || isSubmitting;

	return (
		<>
			{!card && <span>Loading</span>}
			<div ref={cardRef} className={(!card && "hidden") || ""} />
			<div className="mt-4 flex place-content-end">
				<button
					className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary
                           disabled:invisible"
					onClick={handleClick}
					aria-disabled={disabled}
					disabled={disabled}
					type="button"
				>
					Pay $50
				</button>
			</div>
			<div className={message ? "text-red-400 font-medium" : "invisible"}>
				{message}
			</div>
		</>
	);
}

export default SquarePayment;
