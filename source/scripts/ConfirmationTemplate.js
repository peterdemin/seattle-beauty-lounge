export default function renderConfirmation(
	clientName,
	clientEmail,
	clientPhone,
) {
	// embed: 7.03
	return `
<div class="p-6 font-light text-black">
 <span id="h-5ykxqwpjq18w">
 </span>
 <h1 class="py-2 text-2xl text-primary font-light">
  Thank you, ${clientName}!
 </h1>
 <h2 class="py-2 text-xl" id="your-appointment-is-confirmed">
  <span id="h-5ykxqwpjq18w-1">
  </span>
  Your appointment is confirmed.
 </h2>
 <!-- modified_time: 2025-05-03T05:44:42.513Z -->
 <p class="py-2">
  You will receive an email confirmation at ${clientEmail} with the
booking details.
 </p>
 <p class="py-2">
  We'll send a reminder the day before service to ${clientPhone}.
 </p>
 <div class="line-block">
  <div class="line">
   To cancel or reschedule your appointment,
  </div>
  <div class="line">
   call
   <a class="font-medium text-primary underline" href="tel:+13016588708">
    +1 (301) 658-8708
   </a>
  </div>
 </div>
</div>
    `;
}
