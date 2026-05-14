import { NextResponse } from "next/server";
import { hasDemoSession } from "@/lib/api-guards";
import { PROVIDERS } from "@/lib/mock-data";

export const runtime = "nodejs";

export async function GET() {
  if (!(await hasDemoSession())) {
    return NextResponse.json({ message: "Authentication is required." }, { status: 401 });
  }
  return NextResponse.json({ providers: PROVIDERS });
}
