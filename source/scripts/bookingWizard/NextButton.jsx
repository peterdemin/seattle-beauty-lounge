import React from "react";

function NextButton({ handleNext, disabled }) {
	return (
		<div className="flex place-content-end">
			<button
				className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary hover:bg-primary hover:text-neutral disabled:opacity-40 disabled:cursor-not-allowed"
				onClick={handleNext}
				disabled={disabled}
				type="button"
			>
				Next
			</button>
		</div>
	);
}

export default NextButton;
