import { NextResponse } from "next/server";
import { hasDemoSession, isInvalidPayload, readJsonBody } from "@/lib/api-guards";
import { analyzeTriageRequest } from "@/lib/triage";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const body = await readJsonBody(request);
  if (isInvalidPayload(body)) {
    return NextResponse.json({ message: "Please describe the symptoms before running triage." }, { status: 400 });
  }
  if (!(await hasDemoSession())) {
    return NextResponse.json({ message: "Authentication is required." }, { status: 401 });
  }
  if (!body || typeof body.symptoms !== "string" || body.symptoms.trim().length < 3) {
    return NextResponse.json({ message: "Please describe the symptoms before running triage." }, { status: 400 });
  }

  const result = await analyzeTriageRequest({
    symptoms: body.symptoms,
    duration: typeof body.duration === "string" ? body.duration : undefined,
    ageRange: typeof body.ageRange === "string" ? body.ageRange : undefined,
    riskFlags: Array.isArray(body.riskFlags) ? body.riskFlags.map(String) : [],
  });
  return NextResponse.json(result);
}
