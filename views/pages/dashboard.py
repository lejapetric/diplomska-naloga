# views/pages/dashboard.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.calendar_controller import CalendarController
from controllers.onenote_controller import OneNoteController
from controllers.todo_controller import TodoController
from services.background_email_service import BackgroundEmailService

def show_dashboard():
    """Prikaže dashboard za prijavljene uporabnike"""

    st.markdown("# Dashboard")

    
    auth = AuthController()
    user_info = auth.get_user_info()
    access_token = auth.get_access_token()
    
    
    # Gumbi za osvežitev
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    with col1:
        if st.button("🔄 Osveži vse", use_container_width=True, type="primary", help="Ponovno naloži podatke iz Microsoft 365"):
            st.cache_data.clear()
            st.session_state.email_checked = False
            st.success("✅ Podatki se osvežujejo...")
            st.rerun()
    
    with col2:
        if st.button("📧 Preveri e-pošto", use_container_width=True, help="Poišči nove zahteve za sestanke"):
            with st.spinner("Iščem e-pošte z zahtevami za sestanke..."):
                email_service = BackgroundEmailService(access_token)
                new_meetings = email_service.find_and_create_pending_meetings()
                if new_meetings:
                    st.success(f"✅ Najdenih {len(new_meetings)} novih zahtev za sestanek! Pojdite v 'Moji sestanki'.")
                else:
                    st.info("📭 Ni novih zahtev za sestanek")
                st.rerun()
    
    st.markdown("---")
    
    # Hitre akcije
    st.markdown("### ⚡ Hitre akcije")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📅 **Pametni sestanek**\n\nAI bo predlagal termine")
        if st.button("➕ Ustvari sestanek", use_container_width=True, type="primary"):
            st.session_state.page = "smart_meeting"
            st.rerun()
    
    with col2:
        st.info("📁 **Upload zapisnika**\n\nAI bo generiral povzetek")
        if st.button("📤 Naloži datoteko", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    
    with col3:
        st.info("✅ **Microsoft To-Do**\n\nPregled vseh nalog")
        if st.button("📋 Moje naloge", use_container_width=True):
            st.session_state.page = "tasks"
            st.rerun()
    
    st.markdown("---")
    
    # Cache funkcije
    @st.cache_data(ttl=300, show_spinner="Nalaganje sestankov...")
    def get_cached_meetings(token):
        calendar_ctrl = CalendarController(token)
        return calendar_ctrl.get_meetings(limit=5)
    
    @st.cache_data(ttl=300, show_spinner="Nalaganje povzetkov...")
    def get_cached_summaries(token):
        onenote_ctrl = OneNoteController(token)
        return onenote_ctrl.get_all_summaries(limit=5)
    
    @st.cache_data(ttl=300, show_spinner="Nalaganje nalog...")
    def get_cached_tasks(token):
        todo_ctrl = TodoController(token)
        tasks = todo_ctrl.get_all_tasks()
        pending = len([t for t in tasks if t.get('status') != 'completed'])
        return pending, len(tasks)
    
    @st.cache_data(ttl=300, show_spinner="Nalaganje predlogov...")
    def get_cached_pending_meetings(token):
        email_service = BackgroundEmailService(token)
        return email_service.get_pending_meetings()
    
    # Statistika
    st.markdown("### 📊 Statistika")
    
    # Naložimo podatke
    with st.spinner("Pridobivanje podatkov iz Microsoft 365..."):
        meetings = get_cached_meetings(access_token)
        summaries = get_cached_summaries(access_token)
        pending_tasks, total_tasks = get_cached_tasks(access_token)
        pending_meetings = get_cached_pending_meetings(access_token)
    
    # Prikaži statistiko
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        upcoming = len([m for m in meetings if m.get('start', {}).get('dateTime', '')])
        st.metric("📅 Prihajajočih sestankov", upcoming, delta="V koledarju")
    
    with col2:
        st.metric("🤖 AI Povzetkov", len(summaries), delta="V OneNote")
    
    with col3:
        st.metric("✅ Odprtih nalog", pending_tasks, delta=f"Od {total_tasks} skupaj")
    
    with col4:
        st.metric("📧 Čakajočih predlogov", len(pending_meetings), delta="Iz e-pošte")
    
    st.markdown("---")
    
    # Zadnji sestanki
    st.markdown("### 📋 Zadnji sestanki")
    
    if meetings:
        for meeting in meetings[:5]:
            subject = meeting.get("subject", "Brez naslova")
            start = meeting.get("start", {}).get("dateTime", "")
            
            # Formatiraj datum
            if start:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    date_str = dt.strftime("%d.%m.%Y ob %H:%M")
                except:
                    date_str = start[:16]
            else:
                date_str = "Datum neznan"
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{subject}**")
                st.caption(f"📅 {date_str}")
            with col2:
                if st.button(f"📄 Podrobnosti", key=f"meeting_{meeting.get('id')}"):
                    st.session_state.selected_meeting = meeting
                    st.session_state.page = "meetings"
                    st.rerun()
            st.divider()
    else:
        st.info("📭 Ni prihajajočih sestankov v koledarju.")
    
    # Čakajoči predlogi
    if pending_meetings:
        st.markdown("### 📧 Čakajoči predlogi za sestanke")
        
        for meeting in pending_meetings[:3]:
            with st.container():
                st.markdown(f"""
                <span style="background: #e8f0fe; color: #2563eb; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">
                    📧 Iz e-pošte
                </span>
                <br><br>
                <strong>{meeting.get('title', 'Sestanek')}</strong><br>
                🕒 {meeting.get('start_time').strftime('%d.%m.%Y ob %H:%M') if meeting.get('start_time') else 'Datum ni določen'}<br>
                👤 Pošiljatelj: {meeting.get('sender', 'Neznan')}
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Sprejmi", key=f"dashboard_accept_{meeting.get('id')}"):
                        email_service = BackgroundEmailService(access_token)
                        result = email_service.accept_meeting(meeting.get('id'))
                        if result["success"]:
                            st.success("✅ Sestanek sprejet!")
                            st.cache_data.clear()
                            st.rerun()
                
                with col2:
                    if st.button(f"❌ Zavrni", key=f"dashboard_reject_{meeting.get('id')}"):
                        email_service = BackgroundEmailService(access_token)
                        email_service.reject_meeting(meeting.get('id'))
                        st.info("Predlog zavrnjen.")
                        st.cache_data.clear()
                        st.rerun()
                
                st.divider()
        
        if len(pending_meetings) > 3:
            if st.button(f"➕ Prikaži vse ({len(pending_meetings)} predlogov)"):
                st.session_state.page = "meetings"
                st.rerun()