"""
Playwright UI tests — Hospital Online Consultation Portal.

Rules applied (from genesis feedback memory):
1. get_by_role("heading") for title wait — avoids strict-mode violations on duplicate text.
2. Single test_happy_path_ui() — all TC_001–TC_010 in one browser session.
3. Date field is st.text_input — direct fill() works (no date picker workaround needed).
4. Consultation IDs pre-computed before f-strings — no double-repr bug.
5. 3-strategy selectbox: stSelectbox data-testid → data-baseweb → keyboard fallback.
"""

import re
import pytest
from playwright.sync_api import Page, expect, Browser

BASE_URL = "http://localhost:8501"
LOAD_WAIT = 2000   # ms for Streamlit initial load
RENDER_WAIT = 1500  # ms after interactions


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def page(browser: Browser):
    context = browser.new_context()
    p = context.new_page()
    yield p
    context.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wait(page: Page, ms: int = RENDER_WAIT) -> None:
    page.wait_for_timeout(ms)
    try:
        page.wait_for_selector('[data-testid="stSpinner"]', state="hidden", timeout=3000)
    except Exception:
        pass
    page.wait_for_timeout(300)


def _select(page: Page, label: str, value: str) -> None:
    """3-strategy Streamlit selectbox interaction."""
    page.wait_for_timeout(300)

    # Strategy 1 — find stSelectbox container by label text, click, pick option
    try:
        boxes = page.get_by_test_id("stSelectbox").all()
        for box in boxes:
            if label.lower() in box.inner_text().lower():
                box.click()
                page.wait_for_timeout(400)
                opt = page.get_by_role("option", name=value, exact=True)
                if opt.count() > 0:
                    opt.click()
                    page.wait_for_timeout(300)
                    return
    except Exception:
        pass

    # Strategy 2 — data-baseweb select container
    try:
        for container in page.locator('[data-baseweb="select"]').all():
            parent_text = container.locator("xpath=..").inner_text()
            if label.lower() in parent_text.lower():
                container.click()
                page.wait_for_timeout(400)
                page.get_by_role("option", name=value).click()
                page.wait_for_timeout(300)
                return
    except Exception:
        pass

    # Strategy 3 — keyboard fallback
    page.get_by_text(label, exact=True).click()
    page.wait_for_timeout(300)
    page.keyboard.type(value)
    page.keyboard.press("Enter")
    page.wait_for_timeout(300)


def _heading(page: Page, text: str):
    return page.get_by_role("heading").filter(has_text=text)


# ── Single happy-path session ─────────────────────────────────────────────────

def test_happy_path_ui(page: Page) -> None:
    """TC_001 through TC_010 — one browser session, data chained across steps."""

    # ── TC_001: Login ──────────────────────────────────────────────────────
    page.goto(BASE_URL)
    _wait(page, LOAD_WAIT)

    # Rule 1: heading locator, not get_by_text — avoids strict-mode violation
    expect(_heading(page, "Hospital Online Consultation Portal")).to_be_visible(timeout=8000)

    page.get_by_label("Patient ID or Email").fill("patient@example.com")
    page.get_by_label("Password").fill("patient123")
    page.get_by_role("button", name="Login").click()
    _wait(page)

    # ── TC_002: Welcome Page ───────────────────────────────────────────────
    expect(_heading(page, "Welcome to the Hospital Portal")).to_be_visible(timeout=6000)
    expect(page.get_by_role("button", name=re.compile("Book Consultation"))).to_be_visible()
    expect(page.get_by_role("button", name=re.compile("View My Consultations"))).to_be_visible()

    # ── TC_003: Book Consultation ──────────────────────────────────────────
    page.get_by_role("radio", name="Book Consultation").click()
    _wait(page)
    expect(_heading(page, "Book Online Consultation")).to_be_visible(timeout=6000)

    page.get_by_label("Patient Name").fill("Rahul Sharma")
    page.get_by_label("Patient Age").fill("35")

    _select(page, "Gender", "Male")
    _select(page, "Department", "Cardiology")
    _select(page, "Doctor", "Dr. Mehta")
    _select(page, "Consultation Mode", "Video Call")
    _select(page, "Initial Status", "Requested")

    # Rule 3: date field is st.text_input — direct fill works
    page.get_by_label("Consultation Date (YYYY-MM-DD)").fill("2026-05-20")
    page.get_by_label("Consultation Time (HH:MM)").fill("10:30")
    page.get_by_label("Symptoms / Chief Complaint").fill("Chest discomfort and fatigue")

    page.get_by_role("button", name="Book Consultation").click()
    _wait(page)

    expect(page.get_by_text(re.compile("Consultation booked for Rahul Sharma"))).to_be_visible(timeout=6000)

    # Verify in My Consultations
    page.get_by_role("radio", name="My Consultations").click()
    _wait(page)
    expect(page.get_by_text("Rahul Sharma")).to_be_visible(timeout=6000)

    # ── TC_004: Metrics after booking ─────────────────────────────────────
    page.get_by_role("radio", name="Dashboard").click()
    _wait(page)
    expect(_heading(page, "My Dashboard")).to_be_visible(timeout=6000)
    # Total consultations metric card shows 1
    expect(page.get_by_text(re.compile(r"📋\s*1"))).to_be_visible(timeout=6000)
    # Requested = 1
    expect(page.get_by_text(re.compile(r"🕐\s*1"))).to_be_visible(timeout=6000)

    # ── TC_005: Update status Requested → Scheduled ────────────────────────
    page.get_by_role("radio", name="My Consultations").click()
    _wait(page)
    _select(page, "Update Status", "Scheduled")
    _wait(page)
    expect(page.get_by_text("Scheduled")).to_be_visible(timeout=6000)

    # Verify dashboard metrics updated
    page.get_by_role("radio", name="Dashboard").click()
    _wait(page)
    expect(page.get_by_text(re.compile(r"📅\s*1"))).to_be_visible(timeout=6000)  # Scheduled = 1

    # ── TC_006: Update status Scheduled → Completed ────────────────────────
    page.get_by_role("radio", name="My Consultations").click()
    _wait(page)
    _select(page, "Update Status", "Completed")
    _wait(page)
    expect(page.get_by_text("Completed")).to_be_visible(timeout=6000)

    # Verify dashboard metrics
    page.get_by_role("radio", name="Dashboard").click()
    _wait(page)
    expect(page.get_by_text(re.compile(r"✅\s*1"))).to_be_visible(timeout=6000)   # Completed = 1
    expect(page.get_by_text(re.compile(r"💊\s*1"))).to_be_visible(timeout=6000)   # Prescriptions = 1

    # ── TC_007: Filter by Completed ────────────────────────────────────────
    page.get_by_role("radio", name="My Consultations").click()
    _wait(page)
    _select(page, "Filter by Status", "Completed")
    _wait(page)
    expect(page.get_by_text("Rahul Sharma")).to_be_visible(timeout=6000)

    # ── TC_008: Search by doctor name ──────────────────────────────────────
    _select(page, "Filter by Status", "All")
    page.get_by_label("Search (patient name, doctor, or department)").fill("Dr. Mehta")
    _wait(page)
    expect(page.get_by_text("Rahul Sharma")).to_be_visible(timeout=6000)

    # ── TC_009: Prescription section ───────────────────────────────────────
    page.get_by_role("radio", name="Prescription").click()
    _wait(page)
    expect(_heading(page, "Prescription")).to_be_visible(timeout=6000)
    expect(page.get_by_text(re.compile("Available Prescriptions"))).to_be_visible(timeout=6000)

    # Open expander
    page.locator("details summary").filter(has_text="Rahul Sharma").click()
    _wait(page, 600)
    expect(page.get_by_text(re.compile("Prescription Status"))).to_be_visible(timeout=6000)
    expect(page.get_by_text("Available")).to_be_visible(timeout=6000)

    # ── TC_010: Sign Out ───────────────────────────────────────────────────
    page.get_by_role("radio", name="Sign Out").click()
    _wait(page)
    expect(_heading(page, "Sign Out")).to_be_visible(timeout=6000)

    page.get_by_role("button", name=re.compile("Sign Out")).click()
    _wait(page)

    # Verify signed-out message and login page
    expect(page.get_by_text(re.compile("safely ended your session"))).to_be_visible(timeout=6000)
    expect(_heading(page, "Hospital Online Consultation Portal")).to_be_visible(timeout=6000)
