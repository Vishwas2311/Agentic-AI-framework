import pytest
from consultation_logic import (
    authenticate,
    book_consultation,
    filter_consultations,
    search_consultations,
    update_consultation_status_by_id,
    get_metrics,
    get_prescription_summary,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _book(consultations=None, **overrides):
    base = dict(
        patient_name="Rahul Sharma",
        age=35,
        gender="Male",
        department="Cardiology",
        doctor="Dr. Mehta",
        consultation_mode="Video Call",
        consultation_status="Requested",
        date="2026-05-20",
        time="10:30",
        symptoms="Chest discomfort and fatigue",
    )
    base.update(overrides)
    return book_consultation(consultations or [], **base)


# ── authenticate ──────────────────────────────────────────────────────────────

def test_authenticate_valid():
    assert authenticate("patient@example.com", "patient123") is True


def test_authenticate_wrong_password():
    assert authenticate("patient@example.com", "wrong") is False


def test_authenticate_wrong_email():
    assert authenticate("other@example.com", "patient123") is False


def test_authenticate_empty():
    assert authenticate("", "") is False


def test_authenticate_whitespace_email():
    # Whitespace trimmed in authenticate()
    assert authenticate("  patient@example.com  ", "patient123") is True


# ── book_consultation ─────────────────────────────────────────────────────────

def test_book_appends():
    assert len(_book()) == 1


def test_book_fields():
    c = _book()[0]
    assert c["patient_name"] == "Rahul Sharma"
    assert c["department"] == "Cardiology"
    assert c["doctor"] == "Dr. Mehta"
    assert c["consultation_status"] == "Requested"


def test_book_assigns_id():
    c = _book()[0]
    assert "id" in c and len(c["id"]) == 8


def test_book_multiple():
    cs = _book()
    cs = book_consultation(cs, "Priya Iyer", 28, "Female", "Dermatology",
                           "Dr. Rao", "Chat", "Requested", "2026-05-21", "11:00", "Rash")
    assert len(cs) == 2


# ── filter_consultations ──────────────────────────────────────────────────────

def test_filter_all_returns_all():
    cs = _book()
    assert len(filter_consultations(cs, "All")) == 1


def test_filter_matching_status():
    cs = _book()
    assert len(filter_consultations(cs, "Requested")) == 1


def test_filter_non_matching_status():
    cs = _book()
    assert len(filter_consultations(cs, "Completed")) == 0


def test_filter_empty_list():
    assert filter_consultations([], "Requested") == []


def test_filter_scheduled():
    cs = _book(consultation_status="Scheduled")
    assert len(filter_consultations(cs, "Scheduled")) == 1
    assert len(filter_consultations(cs, "Requested")) == 0


# ── search_consultations ──────────────────────────────────────────────────────

def test_search_by_patient_name():
    cs = _book()
    assert len(search_consultations(cs, "Rahul")) == 1


def test_search_by_doctor():
    cs = _book()
    assert len(search_consultations(cs, "Dr. Mehta")) == 1


def test_search_by_department():
    cs = _book()
    assert len(search_consultations(cs, "Cardiology")) == 1


def test_search_case_insensitive():
    cs = _book()
    assert len(search_consultations(cs, "cardiology")) == 1


def test_search_no_match():
    cs = _book()
    assert len(search_consultations(cs, "Neurology")) == 0


def test_search_empty_query():
    cs = _book()
    assert len(search_consultations(cs, "")) == 1


def test_search_empty_list():
    assert search_consultations([], "Rahul") == []


# ── update_consultation_status_by_id ─────────────────────────────────────────

def test_update_status_to_scheduled():
    cs = _book()
    cid = cs[0]["id"]
    result = update_consultation_status_by_id(cs, cid, "Scheduled")
    assert result[0]["consultation_status"] == "Scheduled"


def test_update_status_to_completed():
    cs = _book()
    cid = cs[0]["id"]
    result = update_consultation_status_by_id(cs, cid, "Completed")
    assert result[0]["consultation_status"] == "Completed"


def test_update_status_invalid_id_no_change():
    cs = _book()
    result = update_consultation_status_by_id(cs, "00000000", "Completed")
    assert result[0]["consultation_status"] == "Requested"


def test_update_status_modifies_in_place():
    cs = _book()
    cid = cs[0]["id"]
    returned = update_consultation_status_by_id(cs, cid, "Scheduled")
    # Same list object returned
    assert returned is cs


# ── get_metrics ───────────────────────────────────────────────────────────────

def test_metrics_empty():
    m = get_metrics([])
    assert m == {"total": 0, "requested": 0, "scheduled": 0, "completed": 0, "prescriptions": 0}


def test_metrics_after_booking():
    cs = _book()
    m = get_metrics(cs)
    assert m["total"] == 1
    assert m["requested"] == 1
    assert m["completed"] == 0
    assert m["prescriptions"] == 0


def test_metrics_after_scheduled():
    cs = _book()
    cs = update_consultation_status_by_id(cs, cs[0]["id"], "Scheduled")
    m = get_metrics(cs)
    assert m["scheduled"] == 1
    assert m["requested"] == 0


def test_metrics_after_completion():
    cs = _book()
    cs = update_consultation_status_by_id(cs, cs[0]["id"], "Completed")
    m = get_metrics(cs)
    assert m["completed"] == 1
    assert m["prescriptions"] == 1


def test_metrics_prescriptions_equal_completed():
    cs = _book()
    cs = _book(cs, consultation_status="Completed")
    cs = update_consultation_status_by_id(cs, cs[0]["id"], "Completed")
    m = get_metrics(cs)
    assert m["prescriptions"] == m["completed"]


# ── get_prescription_summary ──────────────────────────────────────────────────

def test_prescription_pending_for_requested():
    cs = _book()
    s = get_prescription_summary(cs[0])
    assert s["status"] == "Pending"
    assert s["doctor_advice"] is None
    assert s["medication_notes"] is None
    assert "disclaimer" in s


def test_prescription_available_for_completed():
    cs = _book()
    cs = update_consultation_status_by_id(cs, cs[0]["id"], "Completed")
    s = get_prescription_summary(cs[0])
    assert s["status"] == "Available"
    assert s["doctor_advice"] is not None
    assert s["medication_notes"] is not None
    assert s["follow_up"] is not None
    assert "disclaimer" in s


def test_prescription_has_demo_disclaimer():
    cs = _book()
    s = get_prescription_summary(cs[0])
    assert "demo" in s["disclaimer"].lower()
