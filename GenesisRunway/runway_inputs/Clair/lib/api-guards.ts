import { readDemoSession } from "./session";

export async function readJsonBody(request: Request): Promise<Record<string, unknown> | null> {
  try {
    const value = await request.json();
    return value && typeof value === "object" && !Array.isArray(value)
      ? (value as Record<string, unknown>)
      : {};
  } catch {
    return null;
  }
}

export function isInvalidPayload(body: Record<string, unknown> | null): boolean {
  return Boolean(body && body.__genesis_invalid_payload === true);
}

export async function hasDemoSession(): Promise<boolean> {
  return Boolean(await readDemoSession());
}
