import { cookies } from "next/headers";
import { DEMO_SESSION, DEMO_USER } from "./mock-data";
import type { DemoSession } from "./types";

export const SESSION_COOKIE = "clair_demo_session";

export function createDemoSession(userId: string): DemoSession {
  return {
    ...DEMO_SESSION,
    id: `session-${userId}-${Date.now()}`,
    userId,
    expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 8).toISOString(),
    uploadedDocumentIds: [],
  };
}

export async function readDemoSession() {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get(SESSION_COOKIE)?.value;
  if (!sessionId) return null;
  return {
    user: DEMO_USER,
    session: { ...DEMO_SESSION, id: sessionId, userId: DEMO_USER.id },
  };
}
