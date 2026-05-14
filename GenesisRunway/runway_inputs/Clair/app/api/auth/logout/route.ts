import { NextResponse } from "next/server";
import { hasDemoSession, isInvalidPayload, readJsonBody } from "@/lib/api-guards";
import { SESSION_COOKIE } from "@/lib/session";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const body = await readJsonBody(request);
  if (isInvalidPayload(body)) {
    return NextResponse.json({ ok: false, message: "Logout does not accept a request body." }, { status: 400 });
  }
  if (!(await hasDemoSession())) {
    return NextResponse.json({ ok: false, message: "Authentication is required." }, { status: 401 });
  }
  const response = NextResponse.json({ ok: true, cleared: ["session", "chat", "uploadedDocuments"] });
  response.cookies.set(SESSION_COOKIE, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });
  return response;
}
