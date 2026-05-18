export type ConsultationStatus =
  | "Requested"
  | "Scheduled"
  | "In Consultation"
  | "Completed"
  | "Cancelled";

export type Gender = "Male" | "Female" | "Other";

export type Department =
  | "General Medicine"
  | "Cardiology"
  | "Dermatology"
  | "Orthopedics"
  | "Pediatrics"
  | "Neurology";

export type Doctor =
  | "Dr. Mehta"
  | "Dr. Sharma"
  | "Dr. Rao"
  | "Dr. Iyer"
  | "Dr. Khan";

export type ConsultationMode = "Video Call" | "Audio Call" | "Chat";

export type PrescriptionStatus = "Pending" | "Available";

export interface Consultation {
  id: string;
  patient_name: string;
  patient_age: number;
  gender: Gender;
  department: Department;
  doctor: Doctor;
  consultation_mode: ConsultationMode;
  consultation_status: ConsultationStatus;
  consultation_date: string;
  consultation_time: string;
  symptoms: string;
  prescription_status: PrescriptionStatus;
  created_at: string;
}

export interface Session {
  isLoggedIn: boolean;
  patientEmail: string;
}

export const DEPARTMENTS: Department[] = [
  "General Medicine",
  "Cardiology",
  "Dermatology",
  "Orthopedics",
  "Pediatrics",
  "Neurology",
];

export const DOCTORS: Doctor[] = [
  "Dr. Mehta",
  "Dr. Sharma",
  "Dr. Rao",
  "Dr. Iyer",
  "Dr. Khan",
];

export const CONSULTATION_MODES: ConsultationMode[] = [
  "Video Call",
  "Audio Call",
  "Chat",
];

export const CONSULTATION_STATUSES: ConsultationStatus[] = [
  "Requested",
  "Scheduled",
  "In Consultation",
  "Completed",
  "Cancelled",
];

export const STATUS_TRANSITIONS: Record<ConsultationStatus, ConsultationStatus[]> = {
  Requested: ["Scheduled", "Cancelled"],
  Scheduled: ["In Consultation", "Completed", "Cancelled"],
  "In Consultation": ["Completed", "Cancelled"],
  Completed: [],
  Cancelled: [],
};
