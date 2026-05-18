# BRD Understanding Summary
## Hospital Online Consultation Portal

**Genesis Session:** hosp-consult-portal-20260507  
**Source:** `migration_inputs/raw_data/Hospital_Online_Consultation_Portal_BRD.docx`  
**Stage:** `brd_understanding_gate` — awaiting human approval  
**Confidence:** 97%

---

## What Genesis Understood

### App Identity
- **Name:** Hospital Online Consultation Portal
- **Domain:** Healthcare (demo, no real patient data)
- **Primary User:** Patient (non-technical)
- **Other Roles:** Admin Staff, Doctor, Customer Support, Care Coordinator

---

### 7 Pages Understood

| # | Page | Layout | Key Components |
|---|------|--------|----------------|
| 1 | Login | Split-screen | Logo, Patient ID/Email, Password, Login Securely button, doctor illustration |
| 2 | Welcome | Sidebar + Hero | Greeting, Book Consultation CTA, View Consultations CTA, 3 info cards, illustration |
| 3 | Dashboard | Sidebar + 4-col metrics + 2×2 actions | Metric cards (Total 12, Scheduled 5, Completed 6, Prescriptions 6), 4 quick-action cards |
| 4 | Book Consultation | Sidebar + Wide form card | 8 fields in 2-col grid + Symptoms textarea + Book button |
| 5 | My Consultations | Sidebar + Filter row + Card list | Search, Status filter, Department filter, consultation cards with status badges + Update |
| 6 | Prescriptions | Sidebar + Status badge + 3 info cards | Prescription Status, Doctor Advice, Medication Notes, Follow-up, Download Placeholder |
| 7 | Sign Out | Sidebar + Centered confirmation | Checkmark, confirmation text, Sign Out Securely button |

---

### Features Understood

- Secure login → session state → dashboard guard (no dashboard before login)
- Live metrics: total, scheduled, completed, prescriptions available
- Consultation booking: patient name, age, gender, department, doctor, mode, date, time, symptoms
- Status update workflow: Requested → Scheduled → In Consultation → Completed → Cancelled
- Filter by status + search by patient name, doctor name, department
- Prescription availability: Available (Completed) or Pending (other statuses)
- Safe sign out with session clear and login redirect
- Demo disclaimer visible throughout

### Data Model
`consultation { id, patient_name, patient_age, gender, department, doctor, consultation_mode, consultation_status, consultation_date, consultation_time, symptoms, prescription_status }`

### Sample Credentials
| Patient ID or Email | Password |
|---|---|
| patient@example.com | patient123 |

### Test Cases
10 happy-path test cases (TC_001–TC_010) covering login, booking, status updates, filter, search, prescriptions, sign out.

### Acceptance Criteria
13 criteria covering all core user journeys.

---

## Visual Design DNA (from Mockups)

| Element | Value |
|---------|-------|
| Layout | Left sidebar (240px) + top header bar + content area |
| Primary color | Teal/Cyan (~#2BB5A0) |
| Background | Light blue-gray (~#F0F4F8) |
| Text | Navy dark (~#1B3A5C) |
| Cards | White, rounded corners, subtle shadow |
| Logo | Teal circle + white plus (+) |
| Status: Scheduled | Teal badge |
| Status: Completed | Green badge |
| CTA Primary | Teal filled button |
| Sign Out | Red/coral filled button |
| Topbar | Teal gradient, logo + title + subtitle left, badge right |

---

## ⚠️ BRD Stack Conflict Detected

**BRD Section 14 says:** `Use Streamlit`  
**Mockups show:** A professional sidebar-nav React/Next.js web application  
**Policy:** NoCode2ProCode blocks prototype stacks for production delivery without explicit human decision

**Genesis cannot proceed to code generation without a delivery mode decision.**

---

## Human Gate — Action Required

See the next section for the delivery mode decision question.
