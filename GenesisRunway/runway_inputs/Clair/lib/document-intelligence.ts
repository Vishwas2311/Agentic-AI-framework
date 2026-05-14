import { completeJson } from "./openai";
import type { DocumentSummary, DocumentSummaryResponse, UploadedDocument } from "./types";

type UploadedDocumentWithText = UploadedDocument & { text: string };

const DOCUMENT_DISCLAIMER =
  "CLAIR provides plain-language document explanation only. It does not diagnose, prescribe treatment, or replace a licensed clinician. Documents are processed in memory only and are not retained.";

type MarkerRule = {
  label: string;
  pattern: RegExp;
  unit: string;
  highAbove?: number;
  lowBelow?: number;
};

const MARKER_RULES: MarkerRule[] = [
  { label: "LDL Cholesterol", pattern: /\bLDL(?:\s+cholesterol)?\D{0,25}(\d+(?:\.\d+)?)/i, unit: "mg/dL", highAbove: 129 },
  { label: "CRP", pattern: /\b(?:CRP|C-reactive protein)\D{0,25}(\d+(?:\.\d+)?)/i, unit: "mg/L", highAbove: 3 },
  { label: "Vitamin D", pattern: /\b(?:Vitamin\s*D|25-OH Vitamin D)\D{0,25}(\d+(?:\.\d+)?|low)/i, unit: "ng/mL", lowBelow: 30 },
  { label: "Glucose", pattern: /\b(?:Glucose|Fasting glucose|Blood sugar)\D{0,25}(\d+(?:\.\d+)?)/i, unit: "mg/dL", highAbove: 125 },
  { label: "HbA1c", pattern: /\b(?:HbA1c|A1c)\D{0,25}(\d+(?:\.\d+)?)/i, unit: "%", highAbove: 5.6 },
  { label: "Hemoglobin", pattern: /\bHemoglobin\D{0,25}(\d+(?:\.\d+)?)/i, unit: "g/dL", lowBelow: 12 },
  { label: "Creatinine", pattern: /\bCreatinine\D{0,25}(\d+(?:\.\d+)?)/i, unit: "mg/dL", highAbove: 1.3 },
  { label: "HDL Cholesterol", pattern: /\bHDL(?:\s+cholesterol)?\D{0,25}(\d+(?:\.\d+)?)/i, unit: "mg/dL", lowBelow: 40 },
];

function compactText(text: string) {
  return text.replace(/\s+/g, " ").trim();
}

function markerStatus(rule: MarkerRule, rawValue: string) {
  if (/low/i.test(rawValue)) return "Low";
  const value = Number(rawValue);
  if (!Number.isFinite(value)) return "Review";
  if (typeof rule.highAbove === "number" && value > rule.highAbove) return value > rule.highAbove * 1.3 ? "High" : "Elevated";
  if (typeof rule.lowBelow === "number" && value < rule.lowBelow) return "Low";
  return "Normal";
}

function formatMarker(rule: MarkerRule, rawValue: string) {
  const value = /low/i.test(rawValue) ? "Low" : `${rawValue} ${rule.unit}`;
  return `${rule.label}: ${value} - ${markerStatus(rule, rawValue)}`;
}

function extractMarkers(text: string) {
  return MARKER_RULES.flatMap((rule) => {
    const match = text.match(rule.pattern);
    return match?.[1] ? [formatMarker(rule, match[1])] : [];
  });
}

function abnormalMarkers(markers: string[]) {
  return markers.filter((marker) => !/\bNormal\b/i.test(marker));
}

function localSummary(document: UploadedDocumentWithText): DocumentSummary {
  const text = compactText(document.text);
  const markers = extractMarkers(text);
  const abnormal = abnormalMarkers(markers);
  const hasEmergencyLanguage = /\b(chest pain|trouble breathing|stroke|severe bleeding|fainting|emergency)\b/i.test(text);

  const keyFindings =
    markers.length > 0
      ? [
          ...abnormal.map((marker) => `${marker}. Discuss this with your clinician.`),
          ...markers.filter((marker) => /\bNormal\b/i.test(marker)).map((marker) => `${marker}.`),
        ].slice(0, 6)
      : [
          "The uploaded PDF text was read successfully.",
          "No common lab marker names were detected automatically, so the report should be reviewed with a clinician.",
        ];

  return {
    plainLanguageSummary:
      abnormal.length > 0
        ? `CLAIR read ${document.fileName} and found ${abnormal.length} item${abnormal.length === 1 ? "" : "s"} that may need discussion with a doctor. These findings are not a diagnosis and should be interpreted with your full medical history.`
        : `CLAIR read ${document.fileName}. The available text did not show obvious emergency language or clearly abnormal common lab markers. Please review the full report with a licensed clinician.`,
    keyFindings,
    actionItems: [
      "Schedule a follow-up with a primary care physician or the ordering clinician.",
      abnormal.length > 0 ? "Discuss the highlighted marker values and whether follow-up testing is needed." : "Ask which values in the report matter most for your health history.",
      "Bring medication, symptom, and previous lab history to the visit.",
      hasEmergencyLanguage ? "If symptoms are urgent or severe, seek emergency care immediately." : "Continue routine monitoring unless symptoms become urgent or severe.",
    ],
    criticalIndicators: markers.length > 0 ? markers : ["No common lab markers were automatically extracted - clinician review recommended"],
    questionsForDoctor: [
      abnormal.length > 0 ? `Which of these results need follow-up: ${abnormal.slice(0, 3).join("; ")}?` : "Which values in this report need attention or follow-up?",
      "Do any results require lifestyle changes, medication, or repeat testing?",
      "When should I repeat this test or schedule the next review?",
    ],
    disclaimer: DOCUMENT_DISCLAIMER,
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function textValue(value: unknown) {
  return typeof value === "string" || typeof value === "number" ? String(value).trim() : "";
}

function indicatorToText(value: unknown) {
  if (typeof value === "string") return value.trim();
  if (!isRecord(value)) return "";

  const label =
    textValue(value.label) ||
    textValue(value.marker) ||
    textValue(value.name) ||
    textValue(value.test) ||
    textValue(value.indicator) ||
    "Report marker";
  const result = textValue(value.value) || textValue(value.result) || textValue(value.measurement);
  const unit = textValue(value.unit);
  const status = textValue(value.status) || textValue(value.interpretation) || textValue(value.flag) || "Review";

  if (result) {
    return `${label}: ${unit && !result.includes(unit) ? `${result} ${unit}` : result} - ${status}`;
  }

  return Object.entries(value)
    .map(([key, entry]) => `${key}: ${textValue(entry)}`)
    .filter((entry) => !entry.endsWith(":"))
    .join("; ");
}

function listToStrings(value: unknown, fallback: string[], formatter = (entry: unknown) => textValue(entry)) {
  if (!Array.isArray(value)) return fallback;
  const items = value.map(formatter).map((item) => item.trim()).filter(Boolean);
  return items.length > 0 ? items : fallback;
}

function normalizeSummary(data: Partial<DocumentSummary>, fallback: DocumentSummary): DocumentSummary {
  return {
    plainLanguageSummary: textValue(data.plainLanguageSummary) || fallback.plainLanguageSummary,
    keyFindings: listToStrings(data.keyFindings, fallback.keyFindings),
    actionItems: listToStrings(data.actionItems, fallback.actionItems),
    criticalIndicators: listToStrings(data.criticalIndicators, fallback.criticalIndicators, indicatorToText),
    questionsForDoctor: listToStrings(data.questionsForDoctor, fallback.questionsForDoctor),
    disclaimer: textValue(data.disclaimer) || fallback.disclaimer,
  };
}

export async function summarizeDocumentText(document: UploadedDocumentWithText): Promise<DocumentSummaryResponse> {
  const fallback = localSummary(document);
  const { data, source, warning } = await completeJson<DocumentSummary>({
    fallback,
    fallbackSource: "local_analysis",
    systemPrompt:
      `You are CLAIR's medical document explanation agent for patients. Summarize only the uploaded document. Use simple English and short point-wise lines. Return valid JSON only with these keys: plainLanguageSummary, keyFindings, actionItems, criticalIndicators, questionsForDoctor, disclaimer. Make plainLanguageSummary a concise patient-friendly paragraph. Make keyFindings an array of clear bullet-style findings from the document. Make actionItems an array of practical follow-up items to discuss with a clinician. Make criticalIndicators an array of strings only, each formatted exactly like "Marker name: value unit - status". Make questionsForDoctor useful and specific. Base every finding on the supplied document text. Do not invent lab values. Do not diagnose, prescribe treatment, or replace a clinician. Always include this disclaimer exactly: "${DOCUMENT_DISCLAIMER}"`,
    userPrompt: JSON.stringify({
      fileName: document.fileName,
      text: document.text.slice(0, 12000),
      locallyExtractedMarkers: fallback.criticalIndicators,
      outputSafety: "Use patient-friendly language. Flag urgent symptoms only as safety cautions.",
    }),
  });
  return { ...normalizeSummary(data, fallback), source, warning, generatedAt: new Date().toISOString() };
}
