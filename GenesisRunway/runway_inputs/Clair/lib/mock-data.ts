import type { DemoSession, DocumentSummary, EmergencySignal, Provider, User } from "./types";

export const DEMO_USER: User = {
  id: "user-patient",
  email: "patient@example.com",
  name: "Maya Rao",
  role: "patient",
};

export const DEMO_SESSION: DemoSession = {
  id: "demo-session",
  userId: DEMO_USER.id,
  expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 8).toISOString(),
  uploadedDocumentIds: [],
};

export const PROVIDERS: Provider[] = [
  {
    id: "provider-cardio-1",
    name: "Dr. Elena Morris",
    specialty: "Cardiology",
    rating: 4.9,
    distanceMiles: 2.4,
    availability: "Today 4:30 PM",
    acceptingPatients: true,
  },
  {
    id: "provider-primary-1",
    name: "Northline Primary Care",
    specialty: "Primary Care",
    rating: 4.8,
    distanceMiles: 1.2,
    availability: "Tomorrow 9:00 AM",
    acceptingPatients: true,
  },
  {
    id: "provider-neuro-1",
    name: "Dr. Samir Khatri",
    specialty: "Neurology",
    rating: 4.7,
    distanceMiles: 4.1,
    availability: "Friday 11:15 AM",
    acceptingPatients: true,
  },
  {
    id: "provider-urgent-1",
    name: "CLAIR Urgent Care Partner",
    specialty: "Urgent Care",
    rating: 4.6,
    distanceMiles: 0.8,
    availability: "Walk-in open",
    acceptingPatients: true,
  },
];

export const EMERGENCY_SIGNALS: EmergencySignal[] = [
  { phrase: "chest pain", severity: "blocking", recommendedAction: "Call emergency services now." },
  { phrase: "trouble breathing", severity: "blocking", recommendedAction: "Seek emergency care immediately." },
  { phrase: "stroke", severity: "blocking", recommendedAction: "Call emergency services now." },
  { phrase: "severe bleeding", severity: "blocking", recommendedAction: "Seek emergency care immediately." },
  { phrase: "fainting", severity: "warning", recommendedAction: "Consider urgent care and monitor symptoms closely." },
];

export const DEMO_DOCUMENT_SUMMARY: DocumentSummary = {
  plainLanguageSummary: "The uploaded document appears to describe routine clinical information. Review it with a licensed clinician for interpretation.",
  keyFindings: ["No emergency language was detected in the demo fallback.", "The document should be discussed with a care professional."],
  actionItems: ["Save questions for the next appointment.", "Bring medication and symptom history if relevant."],
  criticalIndicators: [],
  questionsForDoctor: ["What results matter most?", "Do any findings need follow-up testing?"],
  disclaimer: "CLAIR is not a diagnosis tool. For urgent symptoms, call emergency services.",
};
