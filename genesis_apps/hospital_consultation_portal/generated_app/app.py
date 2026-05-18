import streamlit as st
from consultation_logic import (
    authenticate,
    book_consultation,
    filter_consultations,
    search_consultations,
    update_consultation_status_by_id,
    get_metrics,
    get_prescription_summary,
)

st.set_page_config(
    page_title="Hospital Online Consultation Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS = """
<style>
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }

.metric-card {
    background: #ffffff; border: 1px solid #e8edf2; border-radius: 10px;
    padding: 1.2rem 1.5rem; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,.06); margin-bottom: .5rem;
}
.metric-card .mv { font-size: 2.2rem; font-weight: 700; color: #1a73e8; }
.metric-card .ml { font-size: 0.85rem; color: #6b7280; margin-top: .25rem; }

.consult-card {
    background: #fff; border: 1px solid #e8edf2; border-radius: 10px;
    padding: 1rem 1.25rem; margin-bottom: .5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}

.badge-Requested        { color:#d97706; background:#fffbeb; padding:2px 8px; border-radius:4px; font-size:.8rem; font-weight:600; }
.badge-Scheduled        { color:#2563eb; background:#eff6ff; padding:2px 8px; border-radius:4px; font-size:.8rem; font-weight:600; }
.badge-In-Consultation  { color:#7c3aed; background:#f5f3ff; padding:2px 8px; border-radius:4px; font-size:.8rem; font-weight:600; }
.badge-Completed        { color:#16a34a; background:#f0fdf4; padding:2px 8px; border-radius:4px; font-size:.8rem; font-weight:600; }
.badge-Cancelled        { color:#dc2626; background:#fef2f2; padding:2px 8px; border-radius:4px; font-size:.8rem; font-weight:600; }

.demo-banner {
    background:#fff3cd; border:1px solid #ffc107; border-radius:6px;
    padding:.5rem 1rem; font-size:.8rem; color:#856404; margin-bottom:1rem;
}

.page-hdr { border-bottom:2px solid #e8edf2; padding-bottom:.75rem; margin-bottom:1.5rem; }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

_DEPARTMENTS = ["General Medicine", "Cardiology", "Dermatology", "Orthopedics", "Pediatrics", "Neurology"]
_DOCTORS = ["Dr. Mehta", "Dr. Sharma", "Dr. Rao", "Dr. Iyer", "Dr. Khan"]
_MODES = ["Video Call", "Audio Call", "Chat"]
_STATUSES = ["Requested", "Scheduled", "In Consultation", "Completed", "Cancelled"]
_STATUS_FILTER = ["All"] + _STATUSES


def _init() -> None:
    for k, v in {"logged_in": False, "current_user": None, "consultations": []}.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()


def _demo_banner() -> None:
    st.markdown(
        '<div class="demo-banner">⚠️ Demo system. Do not enter real patient data.</div>',
        unsafe_allow_html=True,
    )


def _badge(status: str) -> str:
    cls = "badge-" + status.replace(" ", "-")
    return f'<span class="{cls}">{status}</span>'


# ── Login ──────────────────────────────────────────────────────────────────────
def page_login() -> None:
    if st.session_state.get("_just_signed_out"):
        st.success("✅ You have safely ended your session. Your session has been cleared.")
        del st.session_state["_just_signed_out"]

    st.markdown(
        "# 🏥 Hospital Online Consultation Portal",
        unsafe_allow_html=False,
    )
    st.markdown(
        "<p style='text-align:center;color:#6b7280;'>Secure Patient Access Portal</p>",
        unsafe_allow_html=True,
    )
    _demo_banner()

    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        with st.form("login_form"):
            st.markdown("#### Patient Sign In")
            email = st.text_input(
                "Patient ID or Email",
                placeholder="patient@example.com",
                key="login_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )
            submitted = st.form_submit_button(
                "Login", use_container_width=True, type="primary"
            )
            st.caption("🔒 Your health data is protected. This is a demo system.")

        if submitted:
            if authenticate(email, password):
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("Invalid credentials. Try: patient@example.com / patient123")

    st.markdown("---")
    st.caption("Need help? Contact hospital support. | Demo: patient@example.com / patient123")


# ── Welcome ────────────────────────────────────────────────────────────────────
def page_welcome() -> None:
    _demo_banner()
    st.markdown(
        f"<div class='page-hdr'><h2>👋 Welcome to the Hospital Portal</h2>"
        f"<p style='color:#6b7280'>Hello, <b>{st.session_state.current_user}</b>! "
        f"How can we help you today?</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style='background:linear-gradient(135deg,#e8f4fd,#f0f9ff);border-radius:12px;
                    padding:2rem;text-align:center;margin-bottom:1.5rem'>
            <div style='font-size:4rem'>🩺</div>
            <h3 style='color:#1a73e8'>Online Doctor Consultation</h3>
            <p style='color:#6b7280'>Connect with our specialist doctors from the comfort of your home.<br>
            Book a consultation, track your appointment, and view your prescription summary.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Book Consultation", use_container_width=True, type="primary", key="welcome_book_btn"):
            st.info("👈 Select 'Book Consultation' from the sidebar to continue.")
    with col2:
        if st.button("📋 View My Consultations", use_container_width=True, key="welcome_view_btn"):
            st.info("👈 Select 'My Consultations' from the sidebar to continue.")

    st.markdown("---")
    st.markdown("##### Hospital Services Available Online")
    services = [
        ("💊", "General Medicine"), ("❤️", "Cardiology"), ("🧴", "Dermatology"),
        ("🦴", "Orthopedics"), ("👶", "Pediatrics"), ("🧠", "Neurology"),
    ]
    cols = st.columns(3)
    for i, (icon, name) in enumerate(services):
        with cols[i % 3]:
            st.markdown(
                f"<div style='background:#fff;border:1px solid #e8edf2;border-radius:8px;"
                f"padding:1rem;text-align:center;margin-bottom:.5rem'>"
                f"<div style='font-size:1.8rem'>{icon}</div><b>{name}</b></div>",
                unsafe_allow_html=True,
            )


# ── Dashboard ─────────────────────────────────────────────────────────────────
def page_dashboard() -> None:
    _demo_banner()
    metrics = get_metrics(st.session_state.consultations)
    st.markdown(
        f"<div class='page-hdr'><h2>📊 My Dashboard</h2>"
        f"<p style='color:#6b7280'>Welcome back, <b>{st.session_state.current_user}</b></p></div>",
        unsafe_allow_html=True,
    )
    m_defs = [
        ("total", "Total Consultations", "📋"),
        ("requested", "Requested", "🕐"),
        ("scheduled", "Scheduled", "📅"),
        ("completed", "Completed", "✅"),
        ("prescriptions", "Prescriptions Available", "💊"),
    ]
    cols = st.columns(5)
    for col, (key, label, icon) in zip(cols, m_defs):
        with col:
            st.markdown(
                f"<div class='metric-card'>"
                f"<div class='mv'>{icon} {metrics[key]}</div>"
                f"<div class='ml'>{label}</div></div>",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Quick Actions")
    q_cols = st.columns(4)
    for col, label in zip(q_cols, ["📅 Book Consultation", "📋 My Consultations", "💊 Prescriptions", "🚪 Sign Out"]):
        with col:
            st.button(label, use_container_width=True, key=f"dash_{label}")


# ── Book Consultation ─────────────────────────────────────────────────────────
def page_book_consultation() -> None:
    _demo_banner()
    st.markdown("<div class='page-hdr'><h2>📅 Book Online Consultation</h2></div>", unsafe_allow_html=True)

    with st.form("book_consultation_form"):
        st.markdown("##### Patient Information")
        c1, c2, c3 = st.columns(3)
        with c1:
            patient_name = st.text_input("Patient Name", placeholder="Enter full name", key="f_name")
        with c2:
            patient_age = st.number_input("Patient Age", min_value=1, max_value=120, value=30, step=1, key="f_age")
        with c3:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="f_gender")

        st.markdown("##### Appointment Details")
        c4, c5 = st.columns(2)
        with c4:
            department = st.selectbox("Department", _DEPARTMENTS, key="f_dept")
        with c5:
            doctor = st.selectbox("Doctor", _DOCTORS, key="f_doctor")

        c6, c7 = st.columns(2)
        with c6:
            mode = st.selectbox("Consultation Mode", _MODES, key="f_mode")
        with c7:
            status = st.selectbox("Initial Status", _STATUSES, index=0, key="f_status")

        c8, c9 = st.columns(2)
        with c8:
            # Use text_input NOT date_input — required for Playwright test compatibility
            date = st.text_input("Consultation Date (YYYY-MM-DD)", placeholder="YYYY-MM-DD", key="f_date")
        with c9:
            time = st.text_input("Consultation Time (HH:MM)", placeholder="10:30", key="f_time")

        symptoms = st.text_area(
            "Symptoms / Chief Complaint",
            placeholder="Describe your symptoms...",
            key="f_symptoms",
            height=100,
        )
        st.caption("All fields are required. This is a demo system — do not enter real patient data.")
        submitted = st.form_submit_button("Book Consultation", use_container_width=True, type="primary")

    if submitted:
        if not patient_name.strip():
            st.error("Patient name is required.")
        elif not date.strip():
            st.error("Consultation date is required.")
        else:
            st.session_state.consultations = book_consultation(
                st.session_state.consultations,
                patient_name.strip(),
                int(patient_age),
                gender,
                department,
                doctor,
                mode,
                status,
                date.strip(),
                time.strip(),
                symptoms.strip(),
            )
            st.success(
                f"✅ Consultation booked for {patient_name} with {doctor} on {date}. "
                f"View it in 'My Consultations'."
            )
            st.balloons()


# ── My Consultations ──────────────────────────────────────────────────────────
def page_my_consultations() -> None:
    _demo_banner()
    st.markdown("<div class='page-hdr'><h2>📋 My Consultations</h2></div>", unsafe_allow_html=True)

    if not st.session_state.consultations:
        st.info("No consultations booked yet. Go to 'Book Consultation' to get started.")
        return

    cf, cs = st.columns([1, 2])
    with cf:
        status_filter = st.selectbox("Filter by Status", _STATUS_FILTER, key="filter_status")
    with cs:
        search_query = st.text_input(
            "Search (patient name, doctor, or department)",
            placeholder="Search...",
            key="search_query",
        )

    displayed = filter_consultations(st.session_state.consultations, status_filter)
    if search_query.strip():
        displayed = search_consultations(displayed, search_query.strip())

    st.markdown(f"**{len(displayed)} consultation(s) found**")
    if not displayed:
        st.warning("No consultations match the current filter / search.")
        return

    for consultation in displayed:
        cid = consultation["id"]
        st.markdown(
            f"<div class='consult-card'>"
            f"<b>👤 {consultation['patient_name']}</b> &nbsp;|&nbsp; "
            f"Age: {consultation['age']} &nbsp;|&nbsp; {consultation['gender']}"
            f" &nbsp;&nbsp; {_badge(consultation['consultation_status'])}<br>"
            f"<small style='color:#6b7280'>"
            f"🏥 {consultation['department']} &nbsp;·&nbsp; "
            f"🩺 {consultation['doctor']} &nbsp;·&nbsp; "
            f"📞 {consultation['consultation_mode']} &nbsp;·&nbsp; "
            f"📅 {consultation['date']} {consultation['time']}"
            f"</small>"
            + (
                f"<br><small style='color:#9ca3af'>Symptoms: {consultation['symptoms']}</small>"
                if consultation.get("symptoms")
                else ""
            )
            + "</div>",
            unsafe_allow_html=True,
        )
        new_status = st.selectbox(
            "Update Status",
            _STATUSES,
            index=_STATUSES.index(consultation["consultation_status"]),
            key=f"update_status_{cid}",
        )
        if new_status != consultation["consultation_status"]:
            st.session_state.consultations = update_consultation_status_by_id(
                st.session_state.consultations, cid, new_status
            )
            st.rerun()
        st.markdown("<hr style='margin:.4rem 0;border-color:#f3f4f6'>", unsafe_allow_html=True)


# ── Prescription ──────────────────────────────────────────────────────────────
def page_prescription() -> None:
    _demo_banner()
    st.markdown(
        "<div class='page-hdr'><h2>💊 Prescription &amp; Medical Summary</h2></div>",
        unsafe_allow_html=True,
    )
    st.info("⚠️ This is a demo prescription summary. Do not enter or use real patient data.")

    if not st.session_state.consultations:
        st.warning("No consultations found. Book a consultation first.")
        return

    completed = [c for c in st.session_state.consultations if c["consultation_status"] == "Completed"]
    pending = [c for c in st.session_state.consultations if c["consultation_status"] != "Completed"]

    if completed:
        st.markdown(f"##### ✅ Available Prescriptions ({len(completed)})")
        for c in completed:
            summ = get_prescription_summary(c)
            with st.expander(f"📄 {c['patient_name']} — {c['doctor']} — {c['date']}"):
                st.markdown(f"**Prescription Status:** {summ['status']}")
                st.markdown(f"**Doctor Advice:** {summ['doctor_advice']}")
                st.markdown(f"**Medication Notes:** {summ['medication_notes']}")
                st.markdown(f"**Follow-Up Recommendation:** {summ['follow_up']}")
                st.caption(summ["disclaimer"])

    if pending:
        st.markdown(f"##### 🕐 Pending Prescriptions ({len(pending)})")
        for c in pending:
            summ = get_prescription_summary(c)
            st.markdown(
                f"- **{c['patient_name']}** — {c['doctor']} — {c['date']} "
                f"— Status: **{c['consultation_status']}** "
                f"— Prescription: _{summ['status']}_"
            )


# ── Sign Out ──────────────────────────────────────────────────────────────────
def page_sign_out() -> None:
    st.markdown("<div class='page-hdr'><h2>🚪 Sign Out</h2></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center;padding:2rem'>"
        f"<div style='font-size:3rem'>👋</div>"
        f"<h3>Ready to sign out?</h3>"
        f"<p style='color:#6b7280'>You are logged in as <b>{st.session_state.current_user}</b>.</p>"
        f"<p style='color:#6b7280'>Please confirm you want to end your session safely.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.button("🚪 Sign Out", use_container_width=True, type="primary", key="sign_out_btn"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.consultations = []
            st.session_state["_just_signed_out"] = True
            st.rerun()
    st.markdown(
        "<div style='text-align:center;margin-top:1rem'>"
        "<small style='color:#6b7280'>🔒 Your session will be cleared securely. "
        "You have safely ended your session.</small></div>",
        unsafe_allow_html=True,
    )


# ── Router ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    page_login()
else:
    _NAV_PAGES = ["Welcome", "Dashboard", "Book Consultation", "My Consultations", "Prescription", "Sign Out"]

    with st.sidebar:
        st.markdown("### 🏥 Hospital Portal")
        st.markdown(f"**Patient:** {st.session_state.current_user}")
        st.markdown("---")
        selected_page = st.radio("Navigation", _NAV_PAGES, key="sidebar_nav")
        st.markdown("---")
        st.caption(f"📋 {len(st.session_state.consultations)} consultation(s)")
        st.caption("Demo system — do not use real patient data")

    _PAGE_FN = {
        "Welcome": page_welcome,
        "Dashboard": page_dashboard,
        "Book Consultation": page_book_consultation,
        "My Consultations": page_my_consultations,
        "Prescription": page_prescription,
        "Sign Out": page_sign_out,
    }
    _PAGE_FN[selected_page]()
