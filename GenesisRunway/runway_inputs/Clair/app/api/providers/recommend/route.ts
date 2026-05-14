import { NextResponse } from "next/server";
import { hasDemoSession, isInvalidPayload, readJsonBody } from "@/lib/api-guards";
import { recommendProviders } from "@/lib/providers";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const body = await readJsonBody(request);
  if (isInvalidPayload(body) || (body && typeof body.specialty !== "string")) {
    return NextResponse.json({ message: "A specialty is required for provider recommendations." }, { status: 400 });
  }
  if (!(await hasDemoSession())) {
    return NextResponse.json({ message: "Authentication is required." }, { status: 401 });
  }
  if (!body) {
    return NextResponse.json({ message: "Provider recommendation payload is required." }, { status: 400 });
  }
  const providers = recommendProviders(String(body?.specialty || ""), String(body?.urgencyLevel || ""));
  return NextResponse.json({ providers });
}
