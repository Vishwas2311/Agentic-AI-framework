import { EMERGENCY_SIGNALS } from "./mock-data";
import { completeJson } from "./openai";
import type { TriageRequest, TriageResponse, TriageResult } from "./types";

const DISCLAIMER = "CLAIR gives educational guidance only and does not diagnose. Call emergency services for urgent or severe symptoms.";

function emergencySignal(symptoms: string) {
  const normalized = symptoms.toLowerCase();
  return EMERGENCY_SIGNALS.find((signal) => normalized.includes(signal.phrase.toLowerCase()));
}

function fallbackTriage(request: TriageRequest): TriageResult {
  const signal = emergencySignal(request.symptoms);
  if (signal?.severity === "blocking") {
    return {
      urgencyLevel: "Emergency",
      suggestedSpecialty: "Emergency Medicine",
      nextStepRecommendation: signal.recommendedAction,
      emergencyOverride: true,
      disclaimer: DISCLAIMER,
    };
  }
  return {
    urgencyLevel: signal ? "Urgent Care" : "Primary Care",
    suggestedSpecialty: signal ? "Urgent Care" : "Primary Care",
    nextStepRecommendation: signal?.recommendedAction || "Book a primary care visit and monitor symptom changes.",
    emergencyOverride: false,
    disclaimer: DISCLAIMER,
  };
}

export async function analyzeTriageRequest(request: TriageRequest): Promise<TriageResponse> {
  const fallback = fallbackTriage(request);
  const { data, source } = await completeJson<TriageResult>({
    fallback,
    systemPrompt:
      "You are a cautious healthcare triage assistant. Return JSON only with urgencyLevel, suggestedSpecialty, nextStepRecommendation, emergencyOverride, and disclaimer. Never diagnose.",
    userPrompt: JSON.stringify({ request, allowedUrgencyLevels: ["Self-care", "Primary Care", "Urgent Care", "Emergency"] }),
  });
  return { ...fallback, ...data, source, generatedAt: new Date().toISOString() };
}
