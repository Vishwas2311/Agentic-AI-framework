import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const samplePdfPath = path.join(process.cwd(), "test-results", "sample-medical-summary.pdf");

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ browser }) => {
  await mkdir(path.dirname(samplePdfPath), { recursive: true });
  const page = await browser.newPage();
  await page.setContent(`
    <!doctype html>
    <html>
      <body style="font-family: Arial, sans-serif; padding: 48px; line-height: 1.6;">
        <h1>Blood Test Report</h1>
        <p>Patient: Maya Rao. Report date: October 24, 2024.</p>
        <p>LDL Cholesterol: 132 mg/dL. CRP: 3.2 mg/L. Vitamin D: 18 ng/mL.</p>
        <p>Glucose: 95 mg/dL. HbA1c: 5.4%.</p>
        <p>No chest pain, trouble breathing, stroke symptoms, or severe bleeding reported.</p>
        <p>This text exists only to verify real document marker extraction and summarization behavior.</p>
      </body>
    </html>
  `);
  await page.pdf({ path: samplePdfPath, format: "Letter", printBackground: true });
  await page.close();
});

async function login(page: import("@playwright/test").Page, nextPath = "/dashboard") {
  await page.goto(`/login?next=${encodeURIComponent(nextPath)}`);
  await page.getByLabel("Email").fill("patient@example.com");
  await page.getByLabel("Access code").fill("patient123");
  await Promise.all([
    page.waitForURL((url) => url.pathname === "/dashboard"),
    page.getByRole("button", { name: /^login$/i }).click(),
  ]);
}

test("CLAIR core routes render", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Clinical AI Navigation Platform/i })).toBeVisible();
  await page.getByRole("link", { name: "Login" }).click();
  await expect(page.getByRole("heading", { name: /Login to CLAIR/i })).toBeVisible();
});

test("workspace routes require login before access", async ({ page, context }) => {
  await context.clearCookies();
  await page.goto("/documents");
  await expect(page).toHaveURL(/\/login\?next=%2Fdocuments/);
  await expect(page.getByRole("heading", { name: /Login to CLAIR/i })).toBeVisible();
});

test("demo login reaches dashboard", async ({ page }) => {
  await login(page);
  await expect.poll(() => new URL(page.url()).pathname).toBe("/dashboard");
  await expect(page.getByRole("heading", { name: /welcome in, maya/i })).toBeVisible();
  await expect(page.getByRole("banner").getByText("Maya Rao")).toBeVisible();
  await expect(page.getByRole("link", { name: "Login" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /logout/i })).toBeVisible();
});

test("document upload summarizes a text-based PDF from the documents screen", async ({ page }) => {
  await login(page, "/documents");
  await expect.poll(() => new URL(page.url()).pathname).toBe("/dashboard");
  await page.goto("/documents");
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: /choose pdf/i }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles(samplePdfPath);
  await expect(page.getByText(/sample-medical-summary\.pdf selected/i)).toBeVisible();
  await page.getByRole("button", { name: /analyze real report/i }).click();

  const summaryText = page.locator('[aria-live="polite"]');
  await expect(summaryText).not.toHaveText(/summarizing document/i, { timeout: 60000 });
  await expect(page.getByText(/key findings/i)).toBeVisible();
  await expect(page.getByText(/OpenAI document agent completed|Local report extraction used|Demo fallback used/i)).toBeVisible();
  await expect(page.locator("main")).toContainText(/LDL/i);
  await expect(page.locator("main")).toContainText("132 mg/dL");
  await expect(page.locator("main")).toContainText("CRP");
  await expect(page.locator("main")).toContainText("3.2 mg/L");
  await expect(page.locator("main")).not.toContainText("[object Object]");
  await expect(page.getByTestId("document-disclaimer")).toBeVisible();
  await expect(page.getByRole("banner").getByText("Maya Rao")).toBeVisible();
  await expect(page.getByRole("link", { name: "Login" })).toHaveCount(0);
});
