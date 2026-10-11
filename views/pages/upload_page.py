# views/pages/upload_page.py
import streamlit as st
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.ai_controller import AIController
from controllers.todo_controller import TodoController
from utils.helpers import parse_attendees, get_file_icon

def show_upload_page():
    st.title("📁 Upload zapisnika ali posnetka")
    
    auth = AuthController()
    
    if not auth.is_authenticated():
        st.warning("Za upload datotek se morate prijaviti")
        return
    
    st.markdown("""
    <div style="background: #f8fafc; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem;">
        <strong>📄 Podprte datoteke:</strong><br>
        • <strong>.txt</strong> - Besedilni zapis sestanka<br>
        • <strong>.vtt</strong> - Teams transkript (WebVTT format)<br>
        • <strong>.mp3</strong> - Posnetek govora (do 25MB) - zahteva dodatno konfiguracijo
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Izberite datoteko", 
        type=['txt', 'vtt', 'mp3'],
        help="Podprti formati: .txt, .vtt, .mp3"
    )
    
    if uploaded_file:
        file_icon = get_file_icon(uploaded_file.name)
        st.success(f"{file_icon} Datoteka '{uploaded_file.name}' uspešno naložena ({uploaded_file.size / 1024:.1f} KB)")
        
        # Opcijski podatki
        st.markdown("---")
        st.markdown("### 📝 Dodatne informacije")
        
        col1, col2 = st.columns(2)
        with col1:
            meeting_title = st.text_input("Naslov sestanka *", value=uploaded_file.name.rsplit('.', 1)[0])
        with col2:
            meeting_date = st.date_input("Datum sestanka", datetime.now())
        
        attendees_input = st.text_area(
            "Udeleženci (opcijsko - vsak email v svojo vrstico)",
            height=80,
            placeholder="ime1@podjetje.si\nime2@podjetje.si"
        )
        
        process_button = st.button("🚀 Obdelaj z AI", use_container_width=True, type="primary")
        
        if process_button and meeting_title:
            attendees = parse_attendees(attendees_input)
            
            # Preberi vsebino datoteke
            with st.spinner("Obdelava datoteke..."):
                content = _extract_text_from_file(uploaded_file)
                
                if content:
                    # Obdelaj z AI in shrani v OneNote
                    ai_ctrl = AIController(auth.get_access_token())
                    
                    result = ai_ctrl.process_and_save_to_onenote(
                        title=meeting_title,
                        content=content,
                        meeting_date=meeting_date.strftime("%d.%m.%Y"),
                        attendees=attendees,
                        file_name=uploaded_file.name
                    )
                    
                    if result["success"]:
                        st.success("✅ Sestanek uspešno obdelan!")
                        
                        # Prikaži povzetek
                        st.markdown("---")
                        st.markdown("### 🤖 AI Povzetek")
                        st.info(result["summary"])
                        
                        # Prikaži naloge
                        if result["action_items"]:
                            st.markdown("### ✅ Izluščene naloge")
                            
                            for item in result["action_items"]:
                                if isinstance(item, dict):
                                    task = item.get("task", "")
                                    assignee = item.get("assignee", "TBD")
                                    due_date = item.get("due_date", "TBD")
                                    st.write(f"- **{task}** (odgovoren: {assignee}, rok: {due_date})")
                                else:
                                    st.write(f"- {item}")
                            
                            # Gumb za dodajanje v To-Do
                            if st.button("📌 Dodaj vse naloge v Microsoft To-Do"):
                                todo_ctrl = TodoController(auth.get_access_token())
                                added = todo_ctrl.add_multiple_tasks(result["action_items"], meeting_title)
                                
                                if added:
                                    st.success(f"✅ {len(added)} nalog dodanih v Microsoft To-Do!")
                                else:
                                    st.warning("Napaka pri dodajanju nalog")
                        
                        # OneNote povezava
                        if result.get("onenote_page"):
                            st.markdown("---")
                            st.markdown("### 📓 Shranjeno v OneNote")
                            
                            if result["onenote_page"].get("url"):
                                st.link_button(
                                    "🔗 Odpri v OneNote",
                                    result["onenote_page"]["url"],
                                    use_container_width=True
                                )
                    else:
                        st.error(result.get("error", "Napaka pri obdelavi"))
                else:
                    st.error("Napaka pri branju datoteke")
        
        elif process_button and not meeting_title:
            st.error("Vnesite naslov sestanka")


def _extract_text_from_file(uploaded_file):
    """Izlušči tekst iz datoteke"""
    file_type = uploaded_file.type
    file_content = uploaded_file.read()
    
    try:
        if file_type == "text/plain":
            return file_content.decode("utf-8")
        
        elif file_type == "text/vtt":
            text = file_content.decode("utf-8")
            # Počisti VTT format
            lines = text.split('\n')
            cleaned = []
            for line in lines:
                line = line.strip()
                if line and not ('-->' in line or line.isdigit() or line.startswith('WEBVTT')):
                    cleaned.append(line)
            return ' '.join(cleaned)
        
        elif "audio" in file_type or uploaded_file.name.endswith('.mp3'):
            return "MP3 obdelava zahteva Azure Speech Services ali Whisper API. Zaenkrat podpiramo samo .txt in .vtt."
        
        else:
            # Poskusi kot tekst
            return file_content.decode("utf-8", errors="ignore")
            
    except Exception as e:
        st.error(f"Napaka pri branju datoteke: {str(e)}")
        return None