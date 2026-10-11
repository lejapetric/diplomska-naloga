# views/pages/email_meetings_page.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.email_controller import EmailController


def show_email_meetings_page():
    st.title("E-pošta → sestanek")
    st.caption("Samodejno ustvarjanje sestankov iz e-pošte")

    auth = AuthController()

    if not auth.is_authenticated():
        st.warning("Za to funkcijo se morate prijaviti")
        return

    st.markdown(
        """
        <div class="callout callout--accent">
            <strong>Kako deluje</strong><br>
            Aplikacija pregleda vašo e-pošto in išče sporočila s prošnjo za sestanek.
            Ko zazna takšno sporočilo, vam predlaga ustvarjanje sestanka v Outlook koledarju.
        </div>
        """,
        unsafe_allow_html=True,
    )

    email_ctrl = EmailController(auth.get_access_token())

    col1, col2 = st.columns([1, 3])
    with col1:
        limit = st.number_input("Število e-poštnih sporočil", min_value=5, max_value=50, value=20)
    with col2:
        st.write("")
        st.write("")
        if st.button("Poišči zahteve za sestanke", use_container_width=True, type="primary"):
            with st.spinner("Analiziram e-pošto..."):
                st.session_state.email_meeting_requests = email_ctrl.find_meeting_requests(limit)
            st.rerun()

    if "email_meeting_requests" not in st.session_state:
        st.markdown(
            '<div class="empty-state">Kliknite "Poišči zahteve za sestanke" za pregled e-pošte.</div>',
            unsafe_allow_html=True,
        )
        return

    meeting_requests = st.session_state.email_meeting_requests

    if not meeting_requests:
        st.markdown(
            '<div class="empty-state">V zadnjih e-poštnih sporočilih ni zahtev za sestanke.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="section-title">Najdenih {len(meeting_requests)} zahtev</div>',
        unsafe_allow_html=True,
    )

    for i, req in enumerate(meeting_requests):
        with st.expander(f"{req.get('subject', 'Brez naslova')} · {req.get('sender', 'Neznan')}"):
            col1, col2 = st.columns(2)

            with col1:
                suggested_date = req.get("suggested_date")
                suggested_time = req.get("suggested_time")
                date_txt = suggested_date.strftime("%d.%m.%Y") if suggested_date else "Ni zaznan (naslednji delovni dan)"
                time_txt = f"{suggested_time[0]:02d}:{suggested_time[1]:02d}" if suggested_time else "Ni zaznana (10:00)"

                st.markdown(
                    f"""
                    <div class="row-meta">Naslov</div><div>{req.get('meeting_title', 'Sestanek')}</div>
                    <div class="row-meta" style="margin-top:.6rem">Pošiljatelj</div><div>{req.get('sender', 'Neznan')}</div>
                    <div class="row-meta" style="margin-top:.6rem">Datum</div><div>{date_txt}</div>
                    <div class="row-meta" style="margin-top:.6rem">Ura</div><div>{time_txt}</div>
                    <div class="row-meta" style="margin-top:.6rem">Trajanje</div><div>{req.get('suggested_duration', 60)} minut</div>
                    <div class="row-meta" style="margin-top:.6rem">Lokacija</div><div>{req.get('suggested_location', 'Microsoft Teams')}</div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown('<div class="row-meta">Udeleženci</div>', unsafe_allow_html=True)
                for attendee in req.get("additional_attendees", []):
                    st.markdown(f"- {attendee}")

            # Streamlit ne dovoli expanderja znotraj expanderja
            st.markdown('<div class="row-meta" style="margin-top:.6rem">Originalno sporočilo</div>', unsafe_allow_html=True)
            st.text(req.get("original_body", "Ni vsebine")[:1000])

            if st.button("Ustvari sestanek", key=f"create_meeting_{i}", type="primary"):
                user_info = auth.get_user_info()
                user_email = user_info.get("mail", user_info.get("userPrincipalName", ""))

                with st.spinner("Ustvarjam sestanek v Outlooku..."):
                    result = email_ctrl.create_meeting_from_email(req, user_email)

                if result["success"]:
                    st.success(f"Sestanek '{result['title']}' je ustvarjen ({result['date'].strftime('%d.%m.%Y ob %H:%M')}).")
                    st.session_state.email_meeting_requests.pop(i)
                    st.rerun()
                else:
                    st.error(f"Napaka: {result.get('error', 'Neznana napaka')}")