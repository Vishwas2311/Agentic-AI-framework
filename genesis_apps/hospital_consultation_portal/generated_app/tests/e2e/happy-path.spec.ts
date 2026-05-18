import { test, expect, Page } from "@playwright/test";

const BASE = "http://localhost:3003";

test.beforeEach(async ({ page }) => {
  await page.goto(BASE);
  await page.evaluate(() => localStorage.removeItem("hosp_portal_state"));
});

async function login(page: Page) {
  await page.goto(BASE);
  await page.fill("#email", "patient@example.com");
  await page.fill("#password", "patient123");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/welcome");
}

// TC_001_LOGIN
test("TC_001 - Login page is visible and patient can log in", async ({ page }) => {
  await page.goto(BASE);
  await expect(page.locator("h1")).toContainText("Hospital Online Consultation Portal");
  await expect(page.locator("#email")).toBeVisible();
  await expect(page.locator("#password")).toBeVisible();
  await page.fill("#email", "patient@example.com");
  await page.fill("#password", "patient123");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/welcome");
  await expect(page.locator("h2")).toContainText("Welcome, Patient");
});

// TC_002_WELCOME
test("TC_002 - Welcome page shows quick actions", async ({ page }) => {
  await login(page);
  await expect(page.getByRole("main").getByRole("link", { name: "Book Consultation" })).toBeVisible();
  await expect(page.getByRole("main").getByRole("link", { name: "View Consultations" })).toBeVisible();
});

// TC_003_BOOK_CONSULTATION
test("TC_003 - Patient can book a consultation", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);

  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.selectOption("#gender", "Male");
  await page.selectOption("#department", "Cardiology");
  await page.selectOption("#doctor", "Dr. Mehta");
  await page.selectOption("#consultation_mode", "Video Call");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.fill("#symptoms", "Chest discomfort and fatigue");
  await page.click('button[type="submit"]');

  await page.waitForURL("**/consultations");
  await expect(page.locator("text=Rahul Sharma")).toBeVisible();
});

// TC_004_METRICS_AFTER_BOOKING
test("TC_004 - Dashboard metrics update after booking", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);
  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/consultations");

  await page.goto(`${BASE}/dashboard`);
  const cards = page.locator(".text-3xl.font-bold.text-teal-600");
  await expect(cards.nth(0)).toContainText("1");
});

// TC_005_UPDATE_STATUS
test("TC_005 - Patient can update consultation status", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);
  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/consultations");

  await page.click('button[aria-label="Update status to Scheduled"]');
  await expect(page.locator("text=Scheduled").first()).toBeVisible();
});

// TC_006_COMPLETE_CONSULTATION
test("TC_006 - Status can be updated to Completed", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);
  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/consultations");

  await page.click('button[aria-label="Update status to Scheduled"]');
  await page.click('button[aria-label="Update status to Completed"]');
  await expect(page.locator("text=Completed").first()).toBeVisible();
});

// TC_007_FILTER_COMPLETED
test("TC_007 - Filter by Completed status works", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);
  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/consultations");

  await page.click('button[aria-label="Update status to Scheduled"]');
  await page.click('button[aria-label="Update status to Completed"]');

  await page.selectOption("#status-filter", "Completed");
  await expect(page.locator("text=Rahul Sharma")).toBeVisible();
});

// TC_008_SEARCH_BY_DOCTOR
test("TC_008 - Search by doctor name works", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);
  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.selectOption("#doctor", "Dr. Mehta");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/consultations");

  await page.fill('input[type="search"]', "Dr. Mehta");
  await expect(page.locator("text=Rahul Sharma")).toBeVisible();
});

// TC_009_PRESCRIPTION
test("TC_009 - Prescription Available after completing consultation", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/book`);
  await page.fill("#patient_name", "Rahul Sharma");
  await page.fill("#patient_age", "35");
  await page.fill("#consultation_date", "2026-05-20");
  await page.fill("#consultation_time", "10:30");
  await page.click('button[type="submit"]');
  await page.waitForURL("**/consultations");

  await page.click('button[aria-label="Update status to Scheduled"]');
  await page.click('button[aria-label="Update status to Completed"]');

  await page.goto(`${BASE}/prescriptions`);
  await expect(page.locator("text=Available for Completed Visit")).toBeVisible();
  await expect(page.locator("text=Doctor Advice")).toBeVisible();
});

// TC_010_SIGN_OUT
test("TC_010 - Patient can sign out and is returned to login", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/signout`);
  await expect(page.getByRole("heading", { name: /sign out/i })).toBeVisible();
  await page.getByRole("button", { name: /sign out securely/i }).click();
  await page.waitForURL(BASE + "/", { timeout: 8000 });
  await expect(page.locator("h1")).toContainText("Hospital Online Consultation Portal");
});
