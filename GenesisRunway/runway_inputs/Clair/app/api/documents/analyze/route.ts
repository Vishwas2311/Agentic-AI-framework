import { NextResponse } from "next/server";
import { hasDemoSession, isInvalidPayload, readJsonBody } from "@/lib/api-guards";
import { summarizeDocumentText } from "@/lib/document-intelligence";
import { extractTextFromPdf, MAX_UPLOAD_BYTES } from "@/lib/pdf";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const contentType = request.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    const body = await readJsonBody(request);
    if (isInvalidPayload(body)) {
      return NextResponse.json({ message: "Upload a PDF file using multipart/form-data." }, { status: 400 });
    }
  }
  if (!(await hasDemoSession())) {
    return NextResponse.json({ message: "Authentication is required." }, { status: 401 });
  }
  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return NextResponse.json({ message: "Upload a PDF file using multipart/form-data." }, { status: 400 });
  }
  const file = form.get("file");
  if (!(file instanceof File)) {
    return NextResponse.json({ message: "Upload a text-based PDF to summarize." }, { status: 400 });
  }
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    return NextResponse.json({ message: "Only PDF files are supported in this release." }, { status: 415 });
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    return NextResponse.json({ message: "PDF must be 4 MB or smaller." }, { status: 413 });
  }

  let text = "";
  try {
    text = await extractTextFromPdf(file);
  } catch {
    return NextResponse.json(
      { message: "This PDF could not be read. Please upload a text-based PDF exported from the source document." },
      { status: 422 }
    );
  }
  if (text.trim().length < 80) {
    return NextResponse.json(
      { message: "This looks like a scanned or image-only PDF. Please upload a text-based PDF." },
      { status: 422 }
    );
  }

  const result = await summarizeDocumentText({
    id: `doc-${Date.now()}`,
    fileName: file.name,
    mimeType: file.type || "application/pdf",
    sizeBytes: file.size,
    textPreview: text.slice(0, 240),
    text,
  });
  return NextResponse.json(result);
}
