# views/pages/meetings_page.py
import re
import streamlit as st
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.calendar_controller import CalendarController
from services.background_email_service import BackgroundEmailService
from utils.helpers import format_datetime


def show_meetings_page():
    auth = AuthController()

    if not auth.is_authenticated():
        st.warning("Za ogled sestankov se morate prijaviti")
        return

    access_token = auth.get_access_token()
    calendar_ctrl = CalendarController(access_token)
    email_service = BackgroundEmailService(access_token)

    # Naslov + akcije
    head, btn1, btn2 = st.columns([4, 1.4, 1])
    with head:
        st.title("Moji sestanki")
        st.caption("Sestanki iz Outlook koledarja in predlogi iz e-pošte")
    with btn1:
        st.write("")
        if st.button("Poišči nove zahteve", use_container_width=True):
            with st.spinner("Iščem e-pošte z zahtevami za sestanke..."):
                new_meetings = email_service.find_and_create_pending_meetings()
            if new_meetings:
                st.success(f"Najdenih {len(new_meetings)} novih zahtev za sestanek.")
            else:
                st.info("Ni novih zahtev za sestanek.")
    with btn2:
        st.write("")
        if st.button("Osveži", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ------------------------------------------------------------------
    # Predlogi iz e-pošte
    # ------------------------------------------------------------------
    pending_meetings = email_service.get_pending_meetings()

    if pending_meetings:
        st.markdown('<div class="section-title">Predlogi iz e-pošte</div>', unsafe_allow_html=True)
        st.caption("Ti sestanki so bili samodejno zaznani v vaši e-pošti. Sprejmite ali zavrnite predlog.")

        for meeting in pending_meetings:
            with st.container(border=True):
                col_info, col_ok, col_no = st.columns([5, 1, 1])

                with col_info:
                    st.markdown(
                        f"""
                        <div class="row-title">{meeting.get('title', 'Sestanek')}<span class="badge">Iz e-pošte</span></div>
                        <div class="row-meta">
                            {meeting.get('start_time').strftime('%d.%m.%Y ob %H:%M')} - {meeting.get('end_time').strftime('%H:%M')}<br>
                            {meeting.get('location', 'Ni lokacije')}<br>
                            Pošiljatelj: {meeting.get('sender', 'Neznan')}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    with st.expander("Originalna e-pošta"):
                        st.text(meeting.get("original_body", "Ni vsebine")[:500])

                with col_ok:
                    if st.button("Sprejmi", key=f"accept_{meeting.get('id')}", type="primary", use_container_width=True):
                        with st.spinner("Ustvarjam sestanek v Outlooku..."):
                            result = email_service.accept_meeting(meeting.get("id"))
                        if result["success"]:
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Napaka: {result.get('error', 'Neznana napaka')}")

                with col_no:
                    if st.button("Zavrni", key=f"reject_{meeting.get('id')}", use_container_width=True):
                        email_service.reject_meeting(meeting.get("id"))
                        st.rerun()

    # ------------------------------------------------------------------
    # Outlook sestanki
    # ------------------------------------------------------------------
    st.markdown('<div class="section-title">Outlook koledar</div>', unsafe_allow_html=True)

    with st.spinner("Nalaganje sestankov iz Outlooka..."):
        meetings = calendar_ctrl.get_meetings(limit=50)

    if not meetings:
        st.markdown('<div class="empty-state">Ni najdenih sestankov v vašem koledarju.</div>', unsafe_allow_html=True)
        return

    filter_option = st.selectbox(
        "Prikaži",
        ["Vsi sestanki", "Prihajajoči sestanki", "Pretekli sestanki", "Teams sestanki"],
    )
    now = datetime.now().isoformat()

    for meeting in meetings:
        subject = meeting.get("subject", "Brez naslova")
        start_time = meeting.get("start", {}).get("dateTime", "")
        location = meeting.get("location", {}).get("displayName", "") or "Ni lokacije"
        is_online = meeting.get("isOnlineMeeting", False)
        meeting_id = meeting.get("id")

        if filter_option == "Prihajajoči sestanki" and start_time < now:
            continue
        if filter_option == "Pretekli sestanki" and start_time > now:
            continue
        if filter_option == "Teams sestanki" and not (is_online or "Teams" in location):
            continue

        badge = '<span class="badge badge--muted">Teams</span>' if (is_online or "Teams" in location) else ""

        with st.container(border=True):
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="row-title">{subject}{badge}</div>
                    <div class="row-meta">{format_datetime(start_time)} · {location}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("Podrobnosti", key=f"details_{meeting_id}", use_container_width=True):
                    st.session_state.selected_meeting_details = meeting_id
                    st.rerun()

    # Podrobnosti izbranega sestanka
    if st.session_state.get("selected_meeting_details"):
        details = calendar_ctrl.get_meeting_details(st.session_state.selected_meeting_details)

        if details:
            st.markdown('<div class="section-title">Podrobnosti sestanka</div>', unsafe_allow_html=True)
            _show_meeting_details(details)

            if st.button("← Nazaj na seznam"):
                st.session_state.selected_meeting_details = None
                st.rerun()


def _show_meeting_details(meeting):
    """Prikaže podrobnosti sestanka"""
    start = meeting.get("start", {}).get("dateTime", "")
    end = meeting.get("end", {}).get("dateTime", "")
    location = meeting.get("location", {}).get("displayName", "Ni lokacije")
    body = meeting.get("body", {}).get("content", "")
    organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("name", "N/A")
    attendees = meeting.get("attendees", [])
    is_online = meeting.get("isOnlineMeeting", False)

    with st.container(border=True):
        st.markdown(f'<div class="row-title" style="font-size:1.1rem;">{meeting.get("subject", "Brez naslova")}</div>',
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div class="row-meta">Čas</div><div>{format_datetime(start)} - {format_datetime(end)}</div>'
                f'<br><div class="row-meta">Lokacija</div><div>{location}</div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(f'<div class="row-meta">Organizator</div><div>{organizer}</div>', unsafe_allow_html=True)
            if is_online:
                join_url = meeting.get("onlineMeeting", {}).get("joinUrl", "")
                if join_url:
                    st.write("")
                    st.link_button("Pridruži se sestanku", join_url)

        if attendees:
            st.markdown('<br><div class="row-meta">Udeleženci</div>', unsafe_allow_html=True)
            for attendee in attendees:
                email = attendee.get("emailAddress", {})
                st.markdown(f"- {email.get('name', 'N/A')} ({email.get('address', '')})")

        if body:
            clean_body = re.sub("<[^<]+?>", "", body).strip()
            if clean_body:
                st.markdown('<div class="row-meta">Opis</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="detail-box">{clean_body}</div>', unsafe_allow_html=True)