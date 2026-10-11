# views/pages/email_meetings_page.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.email_controller import EmailController
from datetime import datetime

def show_email_meetings_page():
    st.title("📧 Samodejno ustvarjanje sestankov iz e-pošte")
    
    auth = AuthController()
    
    if not auth.is_authenticated():
        st.warning("Za to funkcijo se morate prijaviti")
        return
    
    st.markdown("""
    <div style="background: #e8f0fe; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem;">
        <strong>🤖 Kako deluje:</strong><br>
        Aplikacija pregleda vašo e-pošto in išče sporočila, ki vsebujejo prošnje za sestanek.
        Ko zazna takšno sporočilo, vam predlaga ustvarjanje sestanka v Outlook koledarju.
    </div>
    """, unsafe_allow_html=True)
    
    email_ctrl = EmailController(auth.get_access_token())
    
    # Gumb za iskanje
    col1, col2 = st.columns([1, 3])
    with col1:
        limit = st.number_input("Število e-poštnih sporočil", min_value=5, max_value=50, value=20)
    
    with col2:
        if st.button("🔍 Poišči zahteve za sestanke", use_container_width=True, type="primary"):
            with st.spinner("Analiziram e-pošto..."):
                meeting_requests = email_ctrl.find_meeting_requests(limit)
                st.session_state.email_meeting_requests = meeting_requests
                st.rerun()
    
    st.markdown("---")
    
    # Prikaži najdene zahteve
    if st.session_state.get("email_meeting_requests"):
        requests = st.session_state.email_meeting_requests
        
        if not requests:
            st.info("📭 Ni najdenih zahtev za sestanke v zadnjih e-poštnih sporočilih.")
        else:
            st.success(f"✅ Najdenih {len(requests)} zahtev za sestanek")
            
            for i, req in enumerate(requests):
                with st.expander(f"📧 {req.get('subject', 'Brez naslova')} - Od: {req.get('sender', 'Neznan')}"):
                    
                    # Pokaži zaznane podatke
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📝 Zaznani podatki:**")
                        st.write(f"📌 **Naslov:** {req.get('meeting_title', 'Sestanek')}")
                        st.write(f"👤 **Pošiljatelj:** {req.get('sender', 'Neznan')}")
                        
                        if req.get('suggested_date'):
                            st.write(f"📅 **Predlagan datum:** {req['suggested_date'].strftime('%d.%m.%Y')}")
                        else:
                            st.write("📅 **Predlagan datum:** Ni zaznan (bo nastavljen na naslednji delovni dan)")
                        
                        if req.get('suggested_time'):
                            st.write(f"⏰ **Predlagana ura:** {req['suggested_time'][0]:02d}:{req['suggested_time'][1]:02d}")
                        else:
                            st.write("⏰ **Predlagana ura:** Ni zaznana (bo nastavljena na 10:00)")
                        
                        st.write(f"⏱️ **Predlagano trajanje:** {req.get('suggested_duration', 60)} minut")
                        st.write(f"📍 **Lokacija:** {req.get('suggested_location', 'Microsoft Teams')}")
                    
                    with col2:
                        st.markdown("**👥 Udeleženci:**")
                        for attendee in req.get('additional_attendees', []):
                            st.write(f"- {attendee}")
                    
                    # Originalno sporočilo
                    with st.expander("📄 Prikaži originalno sporočilo"):
                        st.text(req.get('original_body', 'Ni vsebine')[:1000])
                    
                    # Gumb za ustvarjanje sestanka
                    if st.button(f"✅ Ustvari sestanek", key=f"create_meeting_{i}", type="primary"):
                        user_info = auth.get_user_info()
                        user_email = user_info.get('mail', user_info.get('userPrincipalName', ''))
                        
                        with st.spinner("Ustvarjam sestanek v Outlooku..."):
                            result = email_ctrl.create_meeting_from_email(req, user_email)
                            
                            if result["success"]:
                                st.success(f"✅ Sestanek '{result['title']}' uspešno ustvarjen!")
                                st.info(f"📅 Datum: {result['date'].strftime('%d.%m.%Y ob %H:%M')}")
                                st.info(f"👥 Udeleženci: {', '.join(result['attendees'])}")
                                st.balloons()
                                
                                # Odstrani ta request iz seznama
                                st.session_state.email_meeting_requests.pop(i)
                                st.rerun()
                            else:
                                st.error(f"❌ Napaka: {result.get('error', 'Neznana napaka')}")
    
    else:
        st.info("🔍 Kliknite 'Poišči zahteve za sestanke' za pregled e-pošte.")