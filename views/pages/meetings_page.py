# views/pages/meetings_page.py
import streamlit as st
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.calendar_controller import CalendarController
from services.background_email_service import BackgroundEmailService
from utils.helpers import format_datetime

def show_meetings_page():
    st.title("📅 Moji sestanki")
    
    auth = AuthController()
    
    if not auth.is_authenticated():
        st.warning("Za ogled sestankov se morate prijaviti")
        return
    
    access_token = auth.get_access_token()
    calendar_ctrl = CalendarController(access_token)
    email_service = BackgroundEmailService(access_token)
    
    # Gumb za ročno iskanje novih e-poštnih zahtev
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col2:
        if st.button("🔍 Poišči nove zahteve", use_container_width=True):
            with st.spinner("Iščem e-pošte z zahtevami za sestanke..."):
                new_meetings = email_service.find_and_create_pending_meetings()
                if new_meetings:
                    st.success(f"✅ Najdenih {len(new_meetings)} novih zahtev za sestanek!")
                else:
                    st.info("📭 Ni novih zahtev za sestanek")
                st.rerun()
    
    with col3:
        if st.button("🔄 Osveži Outlook", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # ============ PENDING SESTANKI (iz e-pošte) ============
    pending_meetings = email_service.get_pending_meetings()
    
    if pending_meetings:
        st.markdown("### 📧 Predlogi za sestanke (iz e-pošte)")
        st.caption("Ti sestanki so bili samodejno zaznani v vaši e-pošti. Sprejmite ali zavrnite predlog.")
        
        for meeting in pending_meetings:
            with st.container():
                # Oznaka da je iz e-pošte
                st.markdown("""
                <span style="background: #e8f0fe; color: #2563eb; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">
                    📧 Generirano iz e-pošte
                </span>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    **📌 {meeting.get('title', 'Sestanek')}**  
                    🕒 {meeting.get('start_time').strftime('%d.%m.%Y ob %H:%M')} - {meeting.get('end_time').strftime('%H:%M')}  
                    📍 {meeting.get('location', 'Ni lokacije')}  
                    👤 Pošiljatelj: {meeting.get('sender', 'Neznan')}
                    """)
                    
                    # Pokaži del e-pošte
                    with st.expander("📄 Prikaži originalno e-pošto"):
                        st.text(meeting.get('original_body', 'Ni vsebine')[:500])
                
                with col2:
                    if st.button("✅ Sprejmi", key=f"accept_{meeting.get('id')}", type="primary"):
                        with st.spinner("Ustvarjam sestanek v Outlooku..."):
                            result = email_service.accept_meeting(meeting.get('id'))
                            if result["success"]:
                                st.success("✅ Sestanek sprejet in dodan v koledar!")
                                st.rerun()
                            else:
                                st.error(f"❌ Napaka: {result.get('error', 'Neznana napaka')}")
                
                with col3:
                    if st.button("❌ Zavrni", key=f"reject_{meeting.get('id')}"):
                        email_service.reject_meeting(meeting.get('id'))
                        st.info("📧 Predlog zavrnjen. E-pošta bo označena kot prebrana.")
                        st.rerun()
                
                st.markdown("---")
    
    # ============ OBSTOJEČI OUTLOOK SESTANKI ============
    st.markdown("### 📅 Sestanki iz Outlook koledarja")
    
    with st.spinner("Nalaganje sestankov iz Outlooka..."):
        meetings = calendar_ctrl.get_meetings(limit=50)
    
    if meetings:
        # Filter
        filter_option = st.selectbox(
            "Prikaži",
            ["Vsi sestanki", "Prihajajoči sestanki", "Pretekli sestanki", "Teams sestanki"]
        )
        
        now = datetime.now().isoformat()
        
        for meeting in meetings:
            subject = meeting.get("subject", "Brez naslova")
            start_time = meeting.get("start", {}).get("dateTime", "")
            location = meeting.get("location", {}).get("displayName", "Ni lokacije")
            is_online = meeting.get("isOnlineMeeting", False)
            meeting_id = meeting.get("id")
            
            # Filtriranje
            if filter_option == "Prihajajoči sestanki" and start_time < now:
                continue
            if filter_option == "Pretekli sestanki" and start_time > now:
                continue
            if filter_option == "Teams sestanki" and not (is_online or "Teams" in location):
                continue
            
            # Formatiraj
            start_display = format_datetime(start_time)
            location_icon = "💻" if is_online or "Teams" in location else "📍"
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="padding: 0.5rem;">
                        <strong style="font-size: 1rem;">📌 {subject}</strong><br>
                        <span style="color: #64748b; font-size: 0.85rem;">
                            🕒 {start_display} &nbsp;|&nbsp;
                            {location_icon} {location}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"📄 Podrobnosti", key=f"details_{meeting_id}"):
                        st.session_state.selected_meeting_details = meeting_id
                        st.rerun()
                
                st.divider()
        
        # Prikaži podrobnosti če so izbrane
        if st.session_state.get("selected_meeting_details"):
            meeting_id = st.session_state.selected_meeting_details
            meeting_details = calendar_ctrl.get_meeting_details(meeting_id)
            
            if meeting_details:
                st.markdown("---")
                st.markdown("### 📋 Podrobnosti sestanka")
                _show_meeting_details(meeting_details)
                
                if st.button("← Nazaj na seznam"):
                    st.session_state.selected_meeting_details = None
                    st.rerun()
    
    else:
        st.info("📭 Ni najdenih sestankov v vašem koledarju")


def _show_meeting_details(meeting):
    """Prikaže podrobnosti sestanka"""
    subject = meeting.get("subject", "Brez naslova")
    start = meeting.get("start", {}).get("dateTime", "")
    end = meeting.get("end", {}).get("dateTime", "")
    location = meeting.get("location", {}).get("displayName", "Ni lokacije")
    body = meeting.get("body", {}).get("content", "Ni opisa")
    organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("name", "N/A")
    attendees = meeting.get("attendees", [])
    is_online = meeting.get("isOnlineMeeting", False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🕒 Čas:**")
        st.write(f"{format_datetime(start)} - {format_datetime(end)}")
        st.write("**📍 Lokacija:**", location)
    
    with col2:
        st.write("**👤 Organizator:**", organizer)
        if is_online:
            join_url = meeting.get("onlineMeeting", {}).get("joinUrl", "")
            if join_url:
                st.link_button("🔗 Pridruži se sestanku", join_url)
    
    st.write("**👥 Udeleženci:**")
    for attendee in attendees:
        email = attendee.get("emailAddress", {})
        name = email.get("name", "N/A")
        address = email.get("address", "")
        st.write(f"- {name} ({address})")
    
    if body and body != "Ni opisa":
        st.write("**📝 Opis:**")
        import re
        clean_body = re.sub('<[^<]+?>', '', body)
        st.markdown(f'<div style="background: #f8fafc; padding: 1rem; border-radius: 10px;">{clean_body}</div>', unsafe_allow_html=True)