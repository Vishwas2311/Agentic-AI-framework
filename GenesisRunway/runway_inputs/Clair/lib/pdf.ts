import { Buffer } from "node:buffer";

export const MAX_UPLOAD_BYTES = 4 * 1024 * 1024;

export async function extractTextFromPdf(file: File) {
  const pdfParse = (await import("pdf-parse")).default;
  const arrayBuffer = await file.arrayBuffer();
  const parsed = await pdfParse(Buffer.from(arrayBuffer));
  return (parsed.text || "").replace(/\s+/g, " ").trim();
}
