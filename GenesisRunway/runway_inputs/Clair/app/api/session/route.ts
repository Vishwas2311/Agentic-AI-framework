import { NextResponse } from "next/server";
import { readDemoSession } from "@/lib/session";

export const runtime = "nodejs";

export async function GET() {
  const session = await readDemoSession();
  if (!session) {
    return NextResponse.json({ authenticated: false, user: null, session: null });
  }
  return NextResponse.json({
    authenticated: true,
    user: session.user,
    session: session.session,
  });
}
