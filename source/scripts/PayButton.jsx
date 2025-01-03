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
		<div>
			<div className="mt-4 flex place-content-end">
				<button
					className="m-6 p-5 aspect-square rounded-full text-2xl text-cyan-400 font-bold nm-convex-stone-200-lg hover:nm-flat-stone-200-lg
                   disabled:invisible"
					onClick={handleClick}
					disabled={loading}
					type="button"
				>
					Pay ${checkout.lineItems[0].unitAmount / 100}
				</button>
			</div>
			{error && <div>{error.message}</div>}
		</div>
	);
};

export default PayButton;
