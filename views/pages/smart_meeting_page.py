# views/pages/smart_meeting_page.py
import streamlit as st
from datetime import datetime, timedelta
from controllers.auth_controller import AuthController
from controllers.calendar_controller import CalendarController
from controllers.ai_controller import AIController
from utils.helpers import parse_attendees

SESSION_KEYS = [
    "meeting_suggestions", "meeting_selected_date", "meeting_title",
    "meeting_attendees", "meeting_description", "meeting_location", "meeting_duration",
]


def _clear_meeting_state():
    for key in SESSION_KEYS:
        st.session_state.pop(key, None)


def show_smart_meeting_page():
    st.title("Pametni sestanek")
    st.caption("AI poišče proste termine za vse udeležence")

    auth = AuthController()

    if not auth.is_authenticated():
        st.warning("Za ustvarjanje sestanka se morate prijaviti")
        return

    if "meeting_suggestions" in st.session_state:
        _show_suggestions(auth)
        return

    with st.form("smart_meeting_form"):
        st.markdown('<div class="section-title" style="margin-top:0">Podatki o sestanku</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Naslov sestanka *", placeholder="npr. Sestanek projektne skupine")
        with col2:
            location = st.selectbox(
                "Lokacija",
                ["Microsoft Teams (online)", "Hybrid (Teams + osebno)", "Sejna soba A", "Sejna soba B", "Drugo"],
            )
            if location == "Drugo":
                location = st.text_input("Vpišite lokacijo")

        st.markdown('<div class="section-title">Udeleženci</div>', unsafe_allow_html=True)
        attendees_input = st.text_area(
            "Emaili udeležencev (vsak v svojo vrstico) *",
            height=100,
            placeholder="ime1@podjetje.si\nime2@podjetje.si",
        )

        st.markdown('<div class="section-title">Datum in trajanje</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            preferred_date = st.date_input(
                "Želeni datum",
                datetime.now() + timedelta(days=1),
                min_value=datetime.now(),
            )
        with col2:
            duration = st.selectbox("Trajanje", [30, 45, 60, 90, 120], index=2, format_func=lambda x: f"{x} minut")

        st.markdown('<div class="section-title">Opis</div>', unsafe_allow_html=True)
        description = st.text_area("Opis (opcijsko)", height=100, placeholder="Dnevni red, točke za diskusijo...")

        btn1, btn2 = st.columns(2)
        with btn1:
            suggest_agenda = st.form_submit_button("AI predlog dnevnega reda", use_container_width=True)
        with btn2:
            submitted = st.form_submit_button("Poišči proste termine", use_container_width=True, type="primary")

        if suggest_agenda:
            if title:
                agenda = AIController().suggest_meeting_agenda(title)
                st.markdown(
                    '<div class="callout callout--accent"><strong>Predlagane točke dnevnega reda</strong></div>',
                    unsafe_allow_html=True,
                )
                for item in agenda:
                    st.write(f"- {item}")
            else:
                st.warning("Najprej vnesite naslov sestanka")

        if submitted:
            if not title:
                st.error("Vnesite naslov sestanka")
                return

            attendees = parse_attendees(attendees_input)
            if not attendees:
                st.error("Vnesite vsaj enega udeleženca")
                return

            user_info = auth.get_user_info()
            user_email = user_info.get("mail", user_info.get("userPrincipalName"))
            if user_email and user_email not in attendees:
                attendees.append(user_email)

            preferred_datetime = datetime.combine(preferred_date, datetime.min.time())
            calendar_ctrl = CalendarController(auth.get_access_token())

            with st.spinner("Preverjanje prostih terminov..."):
                result = calendar_ctrl.suggest_meeting_times(attendees, preferred_datetime, duration)

            if result["status"] in ["success", "alternative"]:
                if result["status"] == "alternative":
                    st.info(result["message"])

                st.session_state.meeting_suggestions = result["suggestions"]
                st.session_state.meeting_selected_date = result["date"]
                st.session_state.meeting_title = title
                st.session_state.meeting_attendees = attendees
                st.session_state.meeting_description = description
                st.session_state.meeting_location = location
                st.session_state.meeting_duration = duration
                st.rerun()
            else:
                st.warning(result["message"])


def _show_suggestions(auth):
    """Prikaže predlagane termine"""
    st.markdown(
        f'<div class="section-title" style="margin-top:0">Predlagani termini za {st.session_state.meeting_selected_date.strftime("%d.%m.%Y")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="callout callout--accent">
            <strong>{st.session_state.meeting_title}</strong><br>
            {st.session_state.meeting_location} · {len(st.session_state.meeting_attendees)} udeležencev
        </div>
        """,
        unsafe_allow_html=True,
    )

    calendar_ctrl = CalendarController(auth.get_access_token())

    for i, slot in enumerate(st.session_state.meeting_suggestions):
        with st.container(border=True):
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f'<div class="row-title">{slot["display"]}</div>'
                    f'<div class="row-meta">{st.session_state.meeting_duration} min</div>',
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("Izberi", key=f"select_{i}", type="primary", use_container_width=True):
                    with st.spinner("Ustvarjanje sestanka..."):
                        event = calendar_ctrl.create_meeting(
                            title=st.session_state.meeting_title,
                            start_time=slot["start"],
                            end_time=slot["end"],
                            attendees=st.session_state.meeting_attendees,
                            location=st.session_state.meeting_location,
                            body=st.session_state.meeting_description,
                        )

                    if event:
                        st.success(f"Sestanek '{st.session_state.meeting_title}' je ustvarjen.")
                        _clear_meeting_state()
                        st.rerun()
                    else:
                        st.error("Sestanka ni bilo mogoče ustvariti.")

    if st.button("← Nazaj na izbiro datuma"):
        _clear_meeting_state()
        st.rerun()