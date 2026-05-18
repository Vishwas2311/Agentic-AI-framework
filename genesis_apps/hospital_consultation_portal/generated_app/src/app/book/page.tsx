"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { AppShell } from "@/components/AppShell";
import { useApp } from "@/context/AppContext";
import {
  Consultation,
  Gender,
  Department,
  Doctor,
  ConsultationMode,
  ConsultationStatus,
  DEPARTMENTS,
  DOCTORS,
  CONSULTATION_MODES,
} from "@/types";

const STATUSES_FOR_BOOKING: ConsultationStatus[] = ["Requested", "Scheduled"];

export default function BookConsultationPage() {
  const { dispatch } = useApp();
  const router = useRouter();

  const [form, setForm] = useState({
    patient_name: "",
    patient_age: "",
    gender: "Male" as Gender,
    department: "General Medicine" as Department,
    doctor: "Dr. Mehta" as Doctor,
    consultation_mode: "Video Call" as ConsultationMode,
    consultation_status: "Requested" as ConsultationStatus,
    consultation_date: "",
    consultation_time: "",
    symptoms: "",
  });

  const [submitted, setSubmitted] = useState(false);

  function set(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const consultation: Consultation = {
      id: uuidv4(),
      patient_name: form.patient_name.trim(),
      patient_age: parseInt(form.patient_age, 10) || 0,
      gender: form.gender,
      department: form.department,
      doctor: form.doctor,
      consultation_mode: form.consultation_mode,
      consultation_status: form.consultation_status,
      consultation_date: form.consultation_date,
      consultation_time: form.consultation_time,
      symptoms: form.symptoms.trim(),
      prescription_status: "Pending",
      created_at: new Date().toISOString(),
    };

    dispatch({ type: "ADD_CONSULTATION", consultation });
    setSubmitted(true);
    setTimeout(() => router.push("/consultations"), 800);
  }

  return (
    <AppShell
      title="Book Online Consultation"
      subtitle="Simple appointment request form for patients."
    >
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 max-w-4xl">
        <h2 className="text-xl font-bold text-navy mb-6">Consultation Details</h2>

        {submitted ? (
          <div className="flex items-center gap-3 bg-teal-50 border border-teal-200 rounded-xl px-5 py-4 text-teal-700 font-semibold text-sm">
            ✓ Consultation booked! Redirecting to My Consultations…
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            {/* Row 1 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <FormField label="Patient Name" htmlFor="patient_name">
                <input
                  id="patient_name"
                  type="text"
                  required
                  value={form.patient_name}
                  onChange={(e) => set("patient_name", e.target.value)}
                  placeholder="Rahul Sharma"
                  className="input"
                />
              </FormField>
              <FormField label="Patient Age" htmlFor="patient_age">
                <input
                  id="patient_age"
                  type="number"
                  min={1}
                  max={120}
                  required
                  value={form.patient_age}
                  onChange={(e) => set("patient_age", e.target.value)}
                  placeholder="35"
                  className="input"
                />
              </FormField>
              <FormField label="Gender" htmlFor="gender">
                <select
                  id="gender"
                  value={form.gender}
                  onChange={(e) => set("gender", e.target.value)}
                  className="input"
                >
                  {(["Male", "Female", "Other"] as Gender[]).map((g) => (
                    <option key={g}>{g}</option>
                  ))}
                </select>
              </FormField>
              <FormField label="Department" htmlFor="department">
                <select
                  id="department"
                  value={form.department}
                  onChange={(e) => set("department", e.target.value)}
                  className="input"
                >
                  {DEPARTMENTS.map((d) => <option key={d}>{d}</option>)}
                </select>
              </FormField>
            </div>

            {/* Row 2 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <FormField label="Doctor" htmlFor="doctor">
                <select
                  id="doctor"
                  value={form.doctor}
                  onChange={(e) => set("doctor", e.target.value)}
                  className="input"
                >
                  {DOCTORS.map((d) => <option key={d}>{d}</option>)}
                </select>
              </FormField>
              <FormField label="Mode" htmlFor="consultation_mode">
                <select
                  id="consultation_mode"
                  value={form.consultation_mode}
                  onChange={(e) => set("consultation_mode", e.target.value)}
                  className="input"
                >
                  {CONSULTATION_MODES.map((m) => <option key={m}>{m}</option>)}
                </select>
              </FormField>
              <FormField label="Date" htmlFor="consultation_date">
                <input
                  id="consultation_date"
                  type="date"
                  required
                  value={form.consultation_date}
                  onChange={(e) => set("consultation_date", e.target.value)}
                  className="input"
                />
              </FormField>
              <FormField label="Time" htmlFor="consultation_time">
                <input
                  id="consultation_time"
                  type="time"
                  required
                  value={form.consultation_time}
                  onChange={(e) => set("consultation_time", e.target.value)}
                  className="input"
                />
              </FormField>
            </div>

            {/* Symptoms */}
            <FormField label="Symptoms" htmlFor="symptoms">
              <textarea
                id="symptoms"
                rows={4}
                value={form.symptoms}
                onChange={(e) => set("symptoms", e.target.value)}
                placeholder="Describe your symptoms…"
                className="input resize-none"
              />
            </FormField>

            <div className="flex items-center gap-4 pt-2">
              <button
                type="submit"
                className="bg-teal-600 hover:bg-teal-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors text-sm"
              >
                Book Consultation
              </button>
              <span className="text-gray-400 text-sm">
                Your request will appear in My Consultations after booking.
              </span>
            </div>
          </form>
        )}
      </div>

      <style jsx global>{`
        .input {
          width: 100%;
          padding: 0.5rem 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          color: #1B3A5C;
          outline: none;
          transition: box-shadow 0.15s;
        }
        .input:focus {
          box-shadow: 0 0 0 2px #2BB5A0;
          border-color: transparent;
        }
      `}</style>
    </AppShell>
  );
}

function FormField({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={htmlFor} className="text-xs font-semibold text-navy">
        {label}
      </label>
      {children}
    </div>
  );
}
