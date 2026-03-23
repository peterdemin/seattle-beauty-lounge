import React, { useMemo, useState } from "react";

import { insertSkips } from "../../availability.js";
import NextButton from "../NextButton.jsx";

function PickTimeslotStep({ slots, date, onTimeslotSelect }) {
	const [selected, setSelected] = useState(null);
	const timeslots = useMemo(() => {
		if (!slots || !date || !slots[date]) {
			return [];
		}
		let skipNumber = 0;
		return insertSkips(slots[date]).map((slot) => {
			if (slot === null) {
				skipNumber += 1;
				return { key: `skip-${date}-${skipNumber}`, slot: null };
			}
			return { key: `slot-${slot}`, slot };
		});
	}, [slots, date]);

	return (
		<div>
			<h2 className="text-2xl text-center pb-4 font-light text-primary">
				Pick a Time
			</h2>
			<div className="grid grid-cols-4 gap-4 mb-4">
				{timeslots.map(({ key, slot }) =>
					slot === null ? (
						<div key={key} />
					) : (
						<button
							onClick={() => {
								setSelected(slot);
							}}
							className={slotClass(slot, selected)}
							type="button"
							key={key}
						>
							{slot}
						</button>
					),
				)}
			</div>
			<NextButton
				handleNext={() => {
					onTimeslotSelect(selected);
				}}
				disabled={!selected}
			/>
		</div>
	);
}

function slotClass(slot, selected) {
	const base =
		"w-full min-w-0 px-1 py-1 rounded-full border-2 text-center whitespace-nowrap text-sm sm:text-base";
	if (selected === slot) {
		return `${base} border-primary text-black font-bold`;
	}
	return `${base} border-neutral text-black`;
}

export default PickTimeslotStep;
