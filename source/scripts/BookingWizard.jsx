import React, { useState, useEffect } from "react";
import ReactDOM from 'react-dom/client';
import { DayPicker } from "react-day-picker";
import "/rdp-style.css";
import { useForm } from "react-hook-form";


function BookingWizard() {
  const [currentStep, setCurrentStep] = useState(1);

  // Wizard State
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [clientName, setClientName] = useState("");
  const [clientPhone, setClientPhone] = useState("");
  const [clientEmail, setClientEmail] = useState("");
  const [paymentInfo, setPaymentInfo] = useState(null);

  // Fetch services on mount
  useEffect(() => {
    async function fetchServices() {
      // const res = await fetch("/api/services");
      // const data = await res.json();
      const data = [
        {
          id: "id",
          name: "name",
          description: "description",
        }
      ];
      setServices(data);
    }
    fetchServices();
  }, []);

  async function handleSubmitAppointment() {
    const payload = {
      serviceId: selectedService,
      date: selectedDate,
      time: selectedTime,
      clientName,
      clientPhone,
      clientEmail,
      // paymentInfo, // If applicable
    };

    const res = await fetch("/api/appointments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      // Success - show confirmation
      setCurrentStep("confirmation");
    } else {
      // Handle errors
      alert("Error submitting appointment");
    }
  }

  // Render steps conditionally:
  return (
    <div>
      {currentStep === 1 && (
        <SelectServiceStep
          services={services}
          onServiceSelect={(id) => {
            setSelectedService(id);
            setCurrentStep(2);
          }}
        />
      )}
      {currentStep === 2 && (
        <PickDateStep
          onDateSelect={(date) => {
            setSelectedDate(date);
            setCurrentStep(3);
          }}
        />
      )}
      {currentStep === 3 && (
        <PickTimeslotStep
          serviceId={selectedService}
          date={selectedDate}
          onTimeslotSelect={(time) => {
            setSelectedTime(time);
            setCurrentStep(4);
          }}
        />
      )}
      {currentStep === 4 && (
        <ClientInfoStep
          clientName={clientName}
          clientPhone={clientPhone}
          clientEmail={clientEmail}
          onNextStep={(name, phone, email) => {
            setClientName(name);
            setClientPhone(phone);
            setClientEmail(email);
            setCurrentStep(5);
          }}
        />
      )}
      {currentStep === 5 && (
        <ReviewAndConfirmStep
          serviceId={selectedService}
          date={selectedDate}
          time={selectedTime}
          clientName={clientName}
          clientPhone={clientPhone}
          clientEmail={clientEmail}
          // paymentInfo={paymentInfo}
          onConfirm={handleSubmitAppointment}
        />
      )}
      {currentStep === "confirmation" && (
        <div>
          <h2>Thank you! Your appointment is confirmed.</h2>
        </div>
      )}
    </div>
  );
}

function SelectServiceStep({ services, onServiceSelect }) {
  return (
    <div>
      <h2>Select a Service</h2>
      <ul>
        {services.map((service) => (
          <li key={service.id}>
            <h3>{service.name}</h3>
            <p>{service.description}</p>
            <button onClick={() => onServiceSelect(service.id)}>
              Select
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}


function PickDateStep({ onDateSelect }) {
  const [selectedDay, setSelectedDay] = useState(null);

  function handleNext() {
    if (selectedDay) {
      onDateSelect(selectedDay);
    }
  }

  return (
    <div>
      <h2>Pick a Date</h2>
      <DayPicker
        mode="single"
        selected={selectedDay}
        onSelect={setSelectedDay}
        // You can add optional props here, like `disabled` or `fromDate/toDate`
        // to limit the selectable date range.
      />

      <button onClick={handleNext} disabled={!selectedDay}>
        Next
      </button>
    </div>
  );
}


function PickTimeslotStep({ serviceId, date, onTimeslotSelect }) {
  const [timeslots, setTimeslots] = useState([]);

  useEffect(() => {
    async function fetchTimes() {
      // const response = await fetch(`/api/services/${serviceId}/availability?date=${date}`);
      // const data = await response.json();
      const data = [
          {time: "07:40", isAvailable: true},
          {time: "12:00", isAvailable: true},
          {time: "17:59", isAvailable: true},
      ];
      setTimeslots(data);
    }
    fetchTimes();
  }, [serviceId, date]);

  return (
    <div>
      <h2>Pick a Time</h2>
      <ul>
        {timeslots.map((slot) => (
          <li key={slot.time}>
            {slot.time}{" "}
            {slot.isAvailable ? (
              <button onClick={() => onTimeslotSelect(slot.time)}>Select</button>
            ) : (
              <span>Not Available</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}


function ClientInfoStep({
  clientName,
  clientPhone,
  clientEmail,
  onNextStep,
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      name: clientName,
      phone: clientPhone,
      email: clientEmail,
    },
  });

  const onSubmit = (data) => {
    onNextStep(data.name, data.phone, data.email);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <h2>Enter Your Information</h2>

      {/* Name */}
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          {...register("name", { required: "Name is required" })}
          placeholder="Your Full Name"
        />
        {errors.name && (
          <p style={{ color: "red" }}>{errors.name.message}</p>
        )}
      </div>

      {/* Phone */}
      <div>
        <label htmlFor="phone">Phone</label>
        <input
          id="phone"
          {...register("phone", {
            required: "Phone number is required",
            pattern: {
              value: /^[\d\s()+-]+$/,
              message: "Invalid phone format",
            },
          })}
          placeholder="e.g. 555-123-4567"
        />
        {errors.phone && (
          <p style={{ color: "red" }}>{errors.phone.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          {...register("email", {
            required: "Email is required",
            pattern: {
              value: /^[^@]+@[^@]+\.[^@]+$/,
              message: "Invalid email format",
            },
          })}
          placeholder="you@example.com"
        />
        {errors.email && (
          <p style={{ color: "red" }}>{errors.email.message}</p>
        )}
      </div>

      <button type="submit">Next</button>
    </form>
  );
}

function ReviewAndConfirmStep({
  serviceId,
  date,
  time,
  clientName,
  clientPhone,
  clientEmail,
  // paymentInfo,
  onConfirm,
}) {
  return (
    <div>
      <h2>Review and Confirm</h2>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Service ID:</strong> {serviceId}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Date:</strong> {date.toString()}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Time:</strong> {time}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Name:</strong> {clientName}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Phone:</strong> {clientPhone}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Email:</strong> {clientEmail}
      </div>

      <button onClick={onConfirm}>Confirm Booking</button>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('book')).render(
  <BookingWizard />
);

export default BookingWizard;
