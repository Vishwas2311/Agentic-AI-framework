export type AiResponseSource = "openai" | "demo_fallback" | "local_analysis";

export interface User {
  id: string;
  email: string;
  name: string;
  role: "patient" | "caregiver" | "care_staff";
}

export interface DemoSession {
  id: string;
  userId: string;
  expiresAt: string;
  uploadedDocumentIds: string[];
}

export interface Provider {
  id: string;
  name: string;
  specialty: string;
  rating: number;
  distanceMiles: number;
  availability: string;
  acceptingPatients: boolean;
}

export interface UploadedDocument {
  id: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  textPreview?: string;
}

export interface DocumentSummary {
  plainLanguageSummary: string;
  keyFindings: string[];
  actionItems: string[];
  criticalIndicators: string[];
  questionsForDoctor: string[];
  disclaimer: string;
}

export interface TriageRequest {
  symptoms: string;
  duration?: string;
  ageRange?: string;
  riskFlags?: string[];
}

export interface TriageResult {
  urgencyLevel: "Self-care" | "Primary Care" | "Urgent Care" | "Emergency";
  suggestedSpecialty: string;
  nextStepRecommendation: string;
  emergencyOverride: boolean;
  disclaimer: string;
}

export interface EmergencySignal {
  phrase: string;
  severity: "blocking" | "warning";
  recommendedAction: string;
}

export type DocumentSummaryResponse = DocumentSummary & { source: AiResponseSource; generatedAt: string; warning?: string };
export type TriageResponse = TriageResult & { source: AiResponseSource; generatedAt: string };
