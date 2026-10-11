# views/pages/smart_meeting_page.py
import streamlit as st
from datetime import datetime, timedelta
from controllers.auth_controller import AuthController
from controllers.calendar_controller import CalendarController
from controllers.ai_controller import AIController
from utils.helpers import parse_attendees, validate_email

def show_smart_meeting_page():
    st.title("➕ Pametno ustvarjanje sestanka")
    
    auth = AuthController()
    
    if not auth.is_authenticated():
        st.warning("Za ustvarjanje sestanka se morate prijaviti")
        return
    
    # Preveri, če smo v koraku izbire termina
    if "meeting_suggestions" in st.session_state:
        _show_suggestions(auth)
        return
    
    with st.form("smart_meeting_form"):
        st.markdown("### 📝 Podatki o sestanku")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Naslov sestanka *", placeholder="npr. Sestanek projektne skupine")
        with col2:
            location = st.selectbox(
                "📍 Lokacija",
                ["Microsoft Teams (online)", "Hybrid (Teams + osebno)", "Sejna soba A", "Sejna soba B", "Drugo"]
            )
            if location == "Drugo":
                location = st.text_input("Vpišite lokacijo")
        
        st.markdown("---")
        st.markdown("### 👥 Udeleženci")
        
        attendees_input = st.text_area(
            "Emaili udeležencev (vsak v svojo vrstico) *",
            height=100,
            placeholder="ime1@podjetje.si\nime2@podjetje.si",
            help="Vnesite email naslove udeležencev, vsak v svojo vrstico"
        )
        
        st.markdown("---")
        st.markdown("### ⏰ Datum in trajanje")
        
        col1, col2 = st.columns(2)
        with col1:
            preferred_date = st.date_input(
                "Želeni datum", 
                datetime.now() + timedelta(days=1),
                min_value=datetime.now()
            )
        with col2:
            duration = st.selectbox("Trajanje", [30, 45, 60, 90, 120], index=2, format_func=lambda x: f"{x} minut")
        
        st.markdown("---")
        st.markdown("### 📋 Opis in dnevni red")
        
        description = st.text_area("Opis (opcijsko)", height=100, placeholder="Dnevni red, točke za diskusijo...")
        
        # AI predlog dnevnega reda
        if st.form_submit_button("🤖 AI predlog dnevnega reda", use_container_width=True):
            if title:
                ai_ctrl = AIController()
                agenda = ai_ctrl.suggest_meeting_agenda(title)
                st.info("Predlagane točke dnevnega reda:")
                for item in agenda:
                    st.write(f"- {item}")
        
        submitted = st.form_submit_button("🔍 Poišči proste termine", use_container_width=True, type="primary")
        
        if submitted:
            if not title:
                st.error("Vnesite naslov sestanka")
                return
            
            attendees = parse_attendees(attendees_input)
            
            if not attendees:
                st.error("Vnesite vsaj enega udeleženca")
                return
            
            # Dodaj trenutnega uporabnika
            user_info = auth.get_user_info()
            user_email = user_info.get('mail', user_info.get('userPrincipalName'))
            if user_email and user_email not in attendees:
                attendees.append(user_email)
            
            preferred_datetime = datetime.combine(preferred_date, datetime.min.time())
            
            calendar_ctrl = CalendarController(auth.get_access_token())
            
            with st.spinner("Preverjanje prostih terminov..."):
                result = calendar_ctrl.suggest_meeting_times(attendees, preferred_datetime, duration)
            
            if result["status"] in ["success", "alternative"]:
                if result["status"] == "alternative":
                    st.info(result["message"])
                
                # Shrani podatke v session state
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
    st.subheader(f"📅 Predlagani termini za {st.session_state.meeting_selected_date.strftime('%A, %d.%m.%Y')}")
    
    st.markdown(f"""
    <div style="background: #e8f0fe; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <strong>📌 {st.session_state.meeting_title}</strong><br>
        📍 {st.session_state.meeting_location}<br>
        👥 {len(st.session_state.meeting_attendees)} udeležencev
    </div>
    """, unsafe_allow_html=True)
    
    calendar_ctrl = CalendarController(auth.get_access_token())
    
    for i, slot in enumerate(st.session_state.meeting_suggestions):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{slot['display']}**")
        with col2:
            st.write(f"{st.session_state.meeting_duration} min")
        with col3:
            if st.button(f"✅ Izberi", key=f"select_{i}", type="primary"):
                with st.spinner("Ustvarjanje sestanka..."):
                    event = calendar_ctrl.create_meeting(
                        title=st.session_state.meeting_title,
                        start_time=slot['start'],
                        end_time=slot['end'],
                        attendees=st.session_state.meeting_attendees,
                        location=st.session_state.meeting_location,
                        body=st.session_state.meeting_description
                    )
                    
                    if event:
                        st.success(f"✅ Sestanek '{st.session_state.meeting_title}' je bil ustvarjen!")
                        st.balloons()
                        
                        # Počisti session state
                        for key in ['meeting_suggestions', 'meeting_selected_date', 'meeting_title', 
                                   'meeting_attendees', 'meeting_description', 'meeting_location', 'meeting_duration']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
        
        st.markdown("---")
    
    if st.button("← Nazaj na izbiro datuma"):
        for key in ['meeting_suggestions', 'meeting_selected_date', 'meeting_title', 
                   'meeting_attendees', 'meeting_description', 'meeting_location', 'meeting_duration']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()