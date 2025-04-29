import * as Square from "@square/web-sdk";
import { useEffect, useRef, useState } from "react";

function SquarePayment({ applicationId, locationId, active, onPayment }) {
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
		onPayment({
			idempotencyKey: idempotencyKey.current,
			token,
		}).then((err) => {
			if (err) {
				console.error(err);
				setMessage(`Failed to book an appointment. Error: ${err}`);
			} else {
				idempotencyKey.current = null;
			}
		});
	};

	return (
		<div className={active ? "" : "hidden"}>
			<h2 className="text-2xl text-center font-light text-primary">
				Put a deposit
			</h2>
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
		card.tokenize().then((result) => {
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
