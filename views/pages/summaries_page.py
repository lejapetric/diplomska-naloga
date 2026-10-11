# views/pages/summaries_page.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.onenote_controller import OneNoteController
from utils.helpers import format_datetime

def show_summaries_page():
    st.title("🤖 AI generirani povzetki")
    
    auth = AuthController()
    
    if not auth.is_authenticated():
        st.warning("Za ogled povzetkov se morate prijaviti")
        return
    
    # Refresh gumb
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Osveži", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    onenote_ctrl = OneNoteController(auth.get_access_token())
    
    with st.spinner("Nalaganje povzetkov iz OneNote..."):
        summaries = onenote_ctrl.get_all_summaries()
    
    if summaries:
        st.success(f"✅ Najdenih {len(summaries)} povzetkov")
        
        for summary in summaries:
            title = summary.get('title', 'Brez naslova')
            created_at = summary.get('created_at', '')
            page_id = summary.get('id')
            web_url = summary.get('web_url')
            
            with st.expander(f"📄 {title}"):
                if created_at:
                    st.caption(f"Ustvarjeno: {format_datetime(created_at)}")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if web_url:
                        st.link_button("🔗 Odpri v OneNote", web_url, use_container_width=True)
                
                with col2:
                    if st.button(f"📋 Kopiraj povezavo", key=f"copy_{page_id}"):
                        st.write(f"Povezava kopirana: {web_url}")
                        st.success("Povezava kopirana!")
    else:
        st.info("📭 Ni povzetkov. Uploadajte zapisnik sestanka!")
        
        if st.button("📤 Naloži prvi zapisnik", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()