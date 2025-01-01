import { useCheckout } from "@stripe/react-stripe-js";
import React from "react";

const PayButton = ({ email, onConfirm }) => {
	const checkout = useCheckout();
	const [loading, setLoading] = React.useState(false);
	const [error, setError] = React.useState(null);

	const handleClick = () => {
		setLoading(true);
		checkout.confirm({ email, redirect: "if_required" }).then((result) => {
			if (result.type === "error") {
				setError(result.error);
			} else {
				onConfirm();
			}
			setLoading(false);
		});
	};

	return (
		<div className="mt-4 flex place-content-end">
			<button
				className="py-2 px-5 rounded-lg text-2xl text-primary font-bold border-2 border-primary
                     hover:bg-primary hover:text-black"
				onClick={handleClick}
				disabled={loading}
				type="button"
			>
				Pay ${checkout.lineItems[0].unitAmount / 100}
			</button>
			{error && <div>{error.message}</div>}
		</div>
	);
};

export default PayButton;
