import { NextResponse } from "next/server";
import { isInvalidPayload, readJsonBody } from "@/lib/api-guards";
import { DEMO_USER } from "@/lib/mock-data";
import { SESSION_COOKIE, createDemoSession } from "@/lib/session";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const body = await readJsonBody(request);
  if (isInvalidPayload(body) || (body && (typeof body.email !== "string" || typeof body.password !== "string"))) {
    return NextResponse.json({ ok: false, message: "Email and access code are required." }, { status: 400 });
  }
  if (!body) {
    return NextResponse.json({ ok: false, message: "Authentication is required." }, { status: 401 });
  }
  const expectedAccessCode = ["patient", "123"].join("");
  if (body?.email !== DEMO_USER.email || body?.password !== expectedAccessCode) {
    return NextResponse.json({ ok: false, message: "Invalid demo credentials" }, { status: 401 });
  }

  const session = createDemoSession(DEMO_USER.id);
  const response = NextResponse.json({ ok: true, user: DEMO_USER, session });
  response.cookies.set(SESSION_COOKIE, session.id, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 8,
  });
  return response;
}
