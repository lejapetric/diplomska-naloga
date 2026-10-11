# views/pages/dashboard.py
from datetime import datetime

import streamlit as st
from controllers.auth_controller import AuthController
from controllers.calendar_controller import CalendarController
from controllers.onenote_controller import OneNoteController
from controllers.todo_controller import TodoController
from services.background_email_service import BackgroundEmailService
from router import router


# ------------------------------------------------------------------
# Cache funkcije (na nivoju modula, da se ne definirajo ob vsakem renderju)
# ------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def get_cached_meetings(token):
    return CalendarController(token).get_meetings(limit=5)


@st.cache_data(ttl=300, show_spinner=False)
def get_cached_summaries(token):
    return OneNoteController(token).get_all_summaries(limit=5)


@st.cache_data(ttl=300, show_spinner=False)
def get_cached_tasks(token):
    tasks = TodoController(token).get_all_tasks()
    pending = len([t for t in tasks if t.get("status") != "completed"])
    return pending, len(tasks)


def _format_start(start):
    if not start:
        return "Datum neznan"
    try:
        dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y ob %H:%M")
    except Exception:
        return start[:16]


def _action_card(col, title, text, label, path, key, primary=False):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="card-title">{title}</div><div class="card-text">{text}</div>',
                unsafe_allow_html=True,
            )
            if st.button(label, key=key, use_container_width=True, type="primary" if primary else "secondary"):
                router.navigate_to(path)


def show_dashboard():
    """Dashboard za prijavljene uporabnike. Stil je v static/style.css."""

    auth = AuthController()
    access_token = auth.get_access_token()
    email_service = BackgroundEmailService(access_token)

    # Naslov + akcije osveževanja
    head, btn1, btn2 = st.columns([4, 1, 1.4])
    with head:
        st.title("Dashboard")
        st.caption("Pregled sestankov, nalog in predlogov iz e-pošte")
    with btn1:
        st.write("")
        if st.button("Osveži", use_container_width=True, help="Ponovno naloži podatke iz Microsoft 365"):
            st.cache_data.clear()
            st.rerun()
    with btn2:
        st.write("")
        if st.button("Preveri e-pošto", use_container_width=True, help="Poišči nove zahteve za sestanke"):
            with st.spinner("Iščem e-pošte z zahtevami za sestanke..."):
                new_meetings = email_service.find_and_create_pending_meetings()
            if new_meetings:
                st.success(f"Najdenih {len(new_meetings)} novih zahtev za sestanek. Odprite 'Moji sestanki'.")
            else:
                st.info("Ni novih zahtev za sestanek.")

    # ------------------------------------------------------------------
    # Hitre akcije
    # ------------------------------------------------------------------
    st.markdown('<div class="section-title">Hitre akcije</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    _action_card(c1, "Pametni sestanek", "AI predlaga proste termine za vse udeležence.",
                 "Ustvari sestanek", "/smart-meeting", "qa_meeting", primary=True)
    _action_card(c2, "Upload zapisnika", "AI iz zapisnika pripravi povzetek in naloge.",
                 "Naloži datoteko", "/upload", "qa_upload")
    _action_card(c3, "Microsoft To-Do", "Pregled vseh nalog iz sestankov.",
                 "Moje naloge", "/tasks", "qa_tasks")

    # ------------------------------------------------------------------
    # Statistika
    # ------------------------------------------------------------------
    st.markdown('<div class="section-title">Statistika</div>', unsafe_allow_html=True)

    with st.spinner("Pridobivanje podatkov iz Microsoft 365..."):
        meetings = get_cached_meetings(access_token)
        summaries = get_cached_summaries(access_token)
        pending_tasks, total_tasks = get_cached_tasks(access_token)
        pending_meetings = email_service.get_pending_meetings()

    m1, m2, m3, m4 = st.columns(4)
    upcoming = len([m for m in meetings if m.get("start", {}).get("dateTime", "")])
    m1.metric("Prihajajoči sestanki", upcoming, delta="V koledarju")
    m2.metric("AI povzetki", len(summaries), delta="V OneNote")
    m3.metric("Odprte naloge", pending_tasks, delta=f"Od {total_tasks} skupaj")
    m4.metric("Čakajoči predlogi", len(pending_meetings), delta="Iz e-pošte")

    # ------------------------------------------------------------------
    # Zadnji sestanki
    # ------------------------------------------------------------------
    st.markdown('<div class="section-title">Zadnji sestanki</div>', unsafe_allow_html=True)

    if meetings:
        for meeting in meetings[:5]:
            subject = meeting.get("subject", "Brez naslova")
            date_str = _format_start(meeting.get("start", {}).get("dateTime", ""))

            with st.container(border=True):
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.markdown(
                        f'<div class="row-title">{subject}</div><div class="row-meta">{date_str}</div>',
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("Podrobnosti", key=f"meeting_{meeting.get('id')}", use_container_width=True):
                        st.session_state.selected_meeting_details = meeting.get("id")
                        router.navigate_to("/meetings")
    else:
        st.markdown('<div class="empty-state">Ni prihajajočih sestankov v koledarju.</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Čakajoči predlogi iz e-pošte
    # ------------------------------------------------------------------
    if pending_meetings:
        st.markdown('<div class="section-title">Čakajoči predlogi za sestanke</div>', unsafe_allow_html=True)

        for meeting in pending_meetings[:3]:
            start_time = meeting.get("start_time")
            when = start_time.strftime("%d.%m.%Y ob %H:%M") if start_time else "Datum ni določen"

            with st.container(border=True):
                col_info, col_ok, col_no = st.columns([5, 1, 1])
                with col_info:
                    st.markdown(
                        f"""
                        <div class="row-title">{meeting.get('title', 'Sestanek')}<span class="badge">Iz e-pošte</span></div>
                        <div class="row-meta">{when}<br>Pošiljatelj: {meeting.get('sender', 'Neznan')}</div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_ok:
                    if st.button("Sprejmi", key=f"dashboard_accept_{meeting.get('id')}",
                                 type="primary", use_container_width=True):
                        result = email_service.accept_meeting(meeting.get("id"))
                        if result["success"]:
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(result.get("error", "Napaka pri ustvarjanju sestanka"))
                with col_no:
                    if st.button("Zavrni", key=f"dashboard_reject_{meeting.get('id')}", use_container_width=True):
                        email_service.reject_meeting(meeting.get("id"))
                        st.rerun()

        if len(pending_meetings) > 3:
            if st.button(f"Prikaži vse ({len(pending_meetings)} predlogov)"):
                router.navigate_to("/meetings")