import OpenAI from "openai";
import type { AiResponseSource } from "./types";

type JsonCompletionInput<T> = {
  systemPrompt: string;
  userPrompt: string;
  fallback: T;
  fallbackSource?: AiResponseSource;
  temperature?: number;
};

let client: OpenAI | null = null;

function openAITimeoutMs() {
  const configured = Number(process.env.OPENAI_TIMEOUT_MS);
  return Number.isFinite(configured) && configured >= 1000 ? configured : 15000;
}

function openAIClient() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return null;
  client ??= new OpenAI({ apiKey, maxRetries: 1, timeout: openAITimeoutMs() });
  return client;
}

function stripCodeFences(value: string) {
  return value.replace(/^```(?:json)?/i, "").replace(/```$/i, "").trim();
}

export async function completeJson<T>({
  systemPrompt,
  userPrompt,
  fallback,
  fallbackSource = "demo_fallback",
  temperature = 0.2,
}: JsonCompletionInput<T>): Promise<{ data: T; source: AiResponseSource; warning?: string }> {
  const openai = openAIClient();
  if (!openai) {
    return { data: fallback, source: fallbackSource, warning: "OPENAI_API_KEY is not configured on the server." };
  }

  try {
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || "gpt-4.1-mini",
      max_completion_tokens: 900,
      temperature,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
    }, {
      timeout: openAITimeoutMs(),
    });
    const text = completion.choices[0]?.message?.content || "";
    return { data: JSON.parse(stripCodeFences(text)) as T, source: "openai" };
  } catch {
    return { data: fallback, source: fallbackSource, warning: "OpenAI analysis could not be completed safely. Showing local extraction instead." };
  }
}
