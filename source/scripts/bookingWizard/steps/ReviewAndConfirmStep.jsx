import React from "react";

import { formatDisplayDate } from "../dateUtils.js";

function ReviewAndConfirmStep({
	serviceTitle,
	date,
	time,
	client,
	error,
	onConfirm,
}) {
	return (
		<div>
			<h2 className="text-2xl text-center font-light text-primary mb-4">
				Review and Confirm
			</h2>
			<table className="table-auto text-lg font-light">
				<tbody>
					<tr>
						<td className="pr-1">Name:</td>
						<td>{client.name}</td>
					</tr>
					<tr>
						<td className="pr-1">Phone:</td>
						<td>{client.phone}</td>
					</tr>
					<tr>
						<td className="pr-1">Email:</td>
						<td>{client.email}</td>
					</tr>
					<tr>
						<td className="pr-1">Service:</td>
						<td>{serviceTitle}</td>
					</tr>
					<tr>
						<td className="pr-1">Date:</td>
						<td>{formatDisplayDate(date)}</td>
					</tr>
					<tr>
						<td className="pr-1">Time:</td>
						<td>{time}</td>
					</tr>
				</tbody>
			</table>
			{error && <p className="mt-4 text-red-600">{error}</p>}
			<div className="mt-4 flex place-content-end">
				<button
					className="mx-2 px-5 aspect-square rounded-full text-2xl text-neutral font-bold bg-primary"
					onClick={onConfirm}
					type="button"
				>
					Confirm
					<br />
					Booking
				</button>
			</div>
		</div>
	);
}

export default ReviewAndConfirmStep;
