import uuid


def authenticate(email: str, password: str) -> bool:
    return email.strip() == "patient@example.com" and password == "patient123"


def _new_id() -> str:
    return str(uuid.uuid4())[:8]


def book_consultation(
    consultations: list,
    patient_name: str,
    age: int,
    gender: str,
    department: str,
    doctor: str,
    consultation_mode: str,
    consultation_status: str,
    date: str,
    time: str,
    symptoms: str,
) -> list:
    consultations.append({
        "id": _new_id(),
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "department": department,
        "doctor": doctor,
        "consultation_mode": consultation_mode,
        "consultation_status": consultation_status,
        "date": date,
        "time": time,
        "symptoms": symptoms,
    })
    return consultations


def get_all_consultations(consultations: list) -> list:
    return consultations


def filter_consultations(consultations: list, status: str) -> list:
    if status == "All":
        return consultations
    return [c for c in consultations if c["consultation_status"] == status]


def search_consultations(consultations: list, query: str) -> list:
    if not query:
        return consultations
    q = query.lower()
    return [
        c for c in consultations
        if q in c["patient_name"].lower()
        or q in c["doctor"].lower()
        or q in c["department"].lower()
    ]


def update_consultation_status_by_id(
    consultations: list, consultation_id: str, new_status: str
) -> list:
    for c in consultations:
        if c["id"] == consultation_id:
            c["consultation_status"] = new_status
            break
    return consultations


def get_metrics(consultations: list) -> dict:
    completed = sum(1 for c in consultations if c["consultation_status"] == "Completed")
    return {
        "total": len(consultations),
        "requested": sum(1 for c in consultations if c["consultation_status"] == "Requested"),
        "scheduled": sum(1 for c in consultations if c["consultation_status"] == "Scheduled"),
        "completed": completed,
        "prescriptions": completed,
    }


def get_prescription_summary(consultation: dict) -> dict:
    if consultation["consultation_status"] == "Completed":
        return {
            "status": "Available",
            "doctor_advice": (
                "Rest adequately and follow the prescribed treatment plan. "
                "This is a demo prescription summary."
            ),
            "medication_notes": (
                "Demo medication: As advised by your doctor. "
                "Do not use without professional consultation."
            ),
            "follow_up": (
                "Follow-up appointment recommended in 2 weeks. "
                "Contact hospital to schedule."
            ),
            "disclaimer": (
                "⚠️ This is a demo prescription summary. "
                "Do not enter or use real patient data."
            ),
        }
    return {
        "status": "Pending",
        "doctor_advice": None,
        "medication_notes": None,
        "follow_up": None,
        "disclaimer": (
            "⚠️ This is a demo prescription summary. "
            "Do not enter or use real patient data."
        ),
    }
