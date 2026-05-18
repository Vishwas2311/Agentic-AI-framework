# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: happy-path.spec.ts >> TC_006 - Status can be updated to Completed
- Location: tests\e2e\happy-path.spec.ts:90:5

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.fill: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('#patient_name')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - alert [ref=e2]
  - generic [ref=e4]:
    - generic [ref=e5]:
      - generic "Hospital logo" [ref=e7]: +
      - heading "Hospital Online Consultation Portal" [level=1] [ref=e8]
      - paragraph [ref=e9]: Secure patient access for virtual consultations, prescriptions, and follow-ups.
      - generic [ref=e10]:
        - generic [ref=e11]:
          - generic [ref=e12]: Patient ID or Email
          - generic [ref=e13]:
            - img [ref=e14]
            - textbox "Patient ID or Email" [ref=e17]:
              - /placeholder: patient@example.com
        - generic [ref=e18]:
          - generic [ref=e19]: Password
          - generic [ref=e20]:
            - img [ref=e21]
            - textbox "Password" [ref=e24]:
              - /placeholder: ••••••••
            - button "Show password" [ref=e25] [cursor=pointer]:
              - img [ref=e26]
        - button "Login Securely" [ref=e29] [cursor=pointer]
      - paragraph [ref=e30]: Demo system. Do not enter real patient data.
    - generic [ref=e31]:
      - paragraph [ref=e41]: Online Doctor Consultation
      - paragraph [ref=e42]: Book virtual consultations from the comfort of your home.
```

# Test source

```ts
  1   | import { test, expect, Page } from "@playwright/test";
  2   | 
  3   | const BASE = "http://localhost:3003";
  4   | 
  5   | test.beforeEach(async ({ page }) => {
  6   |   await page.goto(BASE);
  7   |   await page.evaluate(() => localStorage.removeItem("hosp_portal_state"));
  8   | });
  9   | 
  10  | async function login(page: Page) {
  11  |   await page.goto(BASE);
  12  |   await page.fill("#email", "patient@example.com");
  13  |   await page.fill("#password", "patient123");
  14  |   await page.click('button[type="submit"]');
  15  |   await page.waitForURL("**/welcome");
  16  | }
  17  | 
  18  | // TC_001_LOGIN
  19  | test("TC_001 - Login page is visible and patient can log in", async ({ page }) => {
  20  |   await page.goto(BASE);
  21  |   await expect(page.locator("h1")).toContainText("Hospital Online Consultation Portal");
  22  |   await expect(page.locator("#email")).toBeVisible();
  23  |   await expect(page.locator("#password")).toBeVisible();
  24  |   await page.fill("#email", "patient@example.com");
  25  |   await page.fill("#password", "patient123");
  26  |   await page.click('button[type="submit"]');
  27  |   await page.waitForURL("**/welcome");
  28  |   await expect(page.locator("h2")).toContainText("Welcome, Patient");
  29  | });
  30  | 
  31  | // TC_002_WELCOME
  32  | test("TC_002 - Welcome page shows quick actions", async ({ page }) => {
  33  |   await login(page);
  34  |   await expect(page.getByRole("main").getByRole("link", { name: "Book Consultation" })).toBeVisible();
  35  |   await expect(page.getByRole("main").getByRole("link", { name: "View Consultations" })).toBeVisible();
  36  | });
  37  | 
  38  | // TC_003_BOOK_CONSULTATION
  39  | test("TC_003 - Patient can book a consultation", async ({ page }) => {
  40  |   await login(page);
  41  |   await page.goto(`${BASE}/book`);
  42  | 
  43  |   await page.fill("#patient_name", "Rahul Sharma");
  44  |   await page.fill("#patient_age", "35");
  45  |   await page.selectOption("#gender", "Male");
  46  |   await page.selectOption("#department", "Cardiology");
  47  |   await page.selectOption("#doctor", "Dr. Mehta");
  48  |   await page.selectOption("#consultation_mode", "Video Call");
  49  |   await page.fill("#consultation_date", "2026-05-20");
  50  |   await page.fill("#consultation_time", "10:30");
  51  |   await page.fill("#symptoms", "Chest discomfort and fatigue");
  52  |   await page.click('button[type="submit"]');
  53  | 
  54  |   await page.waitForURL("**/consultations");
  55  |   await expect(page.locator("text=Rahul Sharma")).toBeVisible();
  56  | });
  57  | 
  58  | // TC_004_METRICS_AFTER_BOOKING
  59  | test("TC_004 - Dashboard metrics update after booking", async ({ page }) => {
  60  |   await login(page);
  61  |   await page.goto(`${BASE}/book`);
  62  |   await page.fill("#patient_name", "Rahul Sharma");
  63  |   await page.fill("#patient_age", "35");
  64  |   await page.fill("#consultation_date", "2026-05-20");
  65  |   await page.fill("#consultation_time", "10:30");
  66  |   await page.click('button[type="submit"]');
  67  |   await page.waitForURL("**/consultations");
  68  | 
  69  |   await page.goto(`${BASE}/dashboard`);
  70  |   const cards = page.locator(".text-3xl.font-bold.text-teal-600");
  71  |   await expect(cards.nth(0)).toContainText("1");
  72  | });
  73  | 
  74  | // TC_005_UPDATE_STATUS
  75  | test("TC_005 - Patient can update consultation status", async ({ page }) => {
  76  |   await login(page);
  77  |   await page.goto(`${BASE}/book`);
  78  |   await page.fill("#patient_name", "Rahul Sharma");
  79  |   await page.fill("#patient_age", "35");
  80  |   await page.fill("#consultation_date", "2026-05-20");
  81  |   await page.fill("#consultation_time", "10:30");
  82  |   await page.click('button[type="submit"]');
  83  |   await page.waitForURL("**/consultations");
  84  | 
  85  |   await page.click('button[aria-label="Update status to Scheduled"]');
  86  |   await expect(page.locator("text=Scheduled").first()).toBeVisible();
  87  | });
  88  | 
  89  | // TC_006_COMPLETE_CONSULTATION
  90  | test("TC_006 - Status can be updated to Completed", async ({ page }) => {
  91  |   await login(page);
  92  |   await page.goto(`${BASE}/book`);
> 93  |   await page.fill("#patient_name", "Rahul Sharma");
      |              ^ Error: page.fill: Test timeout of 30000ms exceeded.
  94  |   await page.fill("#patient_age", "35");
  95  |   await page.fill("#consultation_date", "2026-05-20");
  96  |   await page.fill("#consultation_time", "10:30");
  97  |   await page.click('button[type="submit"]');
  98  |   await page.waitForURL("**/consultations");
  99  | 
  100 |   await page.click('button[aria-label="Update status to Scheduled"]');
  101 |   await page.click('button[aria-label="Update status to Completed"]');
  102 |   await expect(page.locator("text=Completed").first()).toBeVisible();
  103 | });
  104 | 
  105 | // TC_007_FILTER_COMPLETED
  106 | test("TC_007 - Filter by Completed status works", async ({ page }) => {
  107 |   await login(page);
  108 |   await page.goto(`${BASE}/book`);
  109 |   await page.fill("#patient_name", "Rahul Sharma");
  110 |   await page.fill("#patient_age", "35");
  111 |   await page.fill("#consultation_date", "2026-05-20");
  112 |   await page.fill("#consultation_time", "10:30");
  113 |   await page.click('button[type="submit"]');
  114 |   await page.waitForURL("**/consultations");
  115 | 
  116 |   await page.click('button[aria-label="Update status to Scheduled"]');
  117 |   await page.click('button[aria-label="Update status to Completed"]');
  118 | 
  119 |   await page.selectOption("#status-filter", "Completed");
  120 |   await expect(page.locator("text=Rahul Sharma")).toBeVisible();
  121 | });
  122 | 
  123 | // TC_008_SEARCH_BY_DOCTOR
  124 | test("TC_008 - Search by doctor name works", async ({ page }) => {
  125 |   await login(page);
  126 |   await page.goto(`${BASE}/book`);
  127 |   await page.fill("#patient_name", "Rahul Sharma");
  128 |   await page.fill("#patient_age", "35");
  129 |   await page.selectOption("#doctor", "Dr. Mehta");
  130 |   await page.fill("#consultation_date", "2026-05-20");
  131 |   await page.fill("#consultation_time", "10:30");
  132 |   await page.click('button[type="submit"]');
  133 |   await page.waitForURL("**/consultations");
  134 | 
  135 |   await page.fill('input[type="search"]', "Dr. Mehta");
  136 |   await expect(page.locator("text=Rahul Sharma")).toBeVisible();
  137 | });
  138 | 
  139 | // TC_009_PRESCRIPTION
  140 | test("TC_009 - Prescription Available after completing consultation", async ({ page }) => {
  141 |   await login(page);
  142 |   await page.goto(`${BASE}/book`);
  143 |   await page.fill("#patient_name", "Rahul Sharma");
  144 |   await page.fill("#patient_age", "35");
  145 |   await page.fill("#consultation_date", "2026-05-20");
  146 |   await page.fill("#consultation_time", "10:30");
  147 |   await page.click('button[type="submit"]');
  148 |   await page.waitForURL("**/consultations");
  149 | 
  150 |   await page.click('button[aria-label="Update status to Scheduled"]');
  151 |   await page.click('button[aria-label="Update status to Completed"]');
  152 | 
  153 |   await page.goto(`${BASE}/prescriptions`);
  154 |   await expect(page.locator("text=Available for Completed Visit")).toBeVisible();
  155 |   await expect(page.locator("text=Doctor Advice")).toBeVisible();
  156 | });
  157 | 
  158 | // TC_010_SIGN_OUT
  159 | test("TC_010 - Patient can sign out and is returned to login", async ({ page }) => {
  160 |   await login(page);
  161 |   await page.goto(`${BASE}/signout`);
  162 |   await expect(page.getByRole("heading", { name: /sign out/i })).toBeVisible();
  163 |   await page.getByRole("button", { name: /sign out securely/i }).click();
  164 |   await page.waitForURL(BASE + "/", { timeout: 8000 });
  165 |   await expect(page.locator("h1")).toContainText("Hospital Online Consultation Portal");
  166 | });
  167 | 
```