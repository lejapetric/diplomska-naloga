# views/pages/upload_page.py
import streamlit as st
from datetime import datetime
from controllers.auth_controller import AuthController
from controllers.ai_controller import AIController
from controllers.todo_controller import TodoController
from utils.helpers import parse_attendees, get_file_icon


def show_upload_page():
    st.title("Upload zapisnika")
    st.caption("AI iz zapisnika ali posnetka pripravi povzetek in naloge")

    auth = AuthController()

    if not auth.is_authenticated():
        st.warning("Za upload datotek se morate prijaviti")
        return

    st.markdown(
        """
        <div class="callout">
            <strong>Podprte datoteke</strong><br>
            .txt - besedilni zapis sestanka<br>
            .vtt - Teams transkript (WebVTT)<br>
            .mp3 - posnetek govora (do 25 MB), zahteva dodatno konfiguracijo
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Izberite datoteko",
        type=["txt", "vtt", "mp3"],
        help="Podprti formati: .txt, .vtt, .mp3",
    )

    if not uploaded_file:
        return

    st.caption(f"{get_file_icon(uploaded_file.name)} {uploaded_file.name} · {uploaded_file.size / 1024:.1f} KB")

    st.markdown('<div class="section-title">Dodatne informacije</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        meeting_title = st.text_input("Naslov sestanka *", value=uploaded_file.name.rsplit(".", 1)[0])
    with col2:
        meeting_date = st.date_input("Datum sestanka", datetime.now())

    attendees_input = st.text_area(
        "Udeleženci (opcijsko - vsak email v svojo vrstico)",
        height=80,
        placeholder="ime1@podjetje.si\nime2@podjetje.si",
    )

    process_button = st.button("Obdelaj z AI", use_container_width=True, type="primary")

    if process_button and not meeting_title:
        st.error("Vnesite naslov sestanka")
        return

    if process_button and meeting_title:
        attendees = parse_attendees(attendees_input)

        with st.spinner("Obdelava datoteke..."):
            content = _extract_text_from_file(uploaded_file)

            if not content:
                st.error("Napaka pri branju datoteke")
                return

            ai_ctrl = AIController(auth.get_access_token())
            result = ai_ctrl.process_and_save_to_onenote(
                title=meeting_title,
                content=content,
                meeting_date=meeting_date.strftime("%d.%m.%Y"),
                attendees=attendees,
                file_name=uploaded_file.name,
            )

        if not result["success"]:
            st.error(result.get("error", "Napaka pri obdelavi"))
            return

        st.success("Sestanek je obdelan.")

        st.markdown('<div class="section-title">AI povzetek</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.write(result["summary"])

        if result["action_items"]:
            st.markdown('<div class="section-title">Izluščene naloge</div>', unsafe_allow_html=True)
            with st.container(border=True):
                for item in result["action_items"]:
                    if isinstance(item, dict):
                        st.markdown(
                            f"- **{item.get('task', '')}** "
                            f"<span class='row-meta'>({item.get('assignee', 'TBD')}, rok: {item.get('due_date', 'TBD')})</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(f"- {item}")

            if st.button("Dodaj vse naloge v Microsoft To-Do"):
                todo_ctrl = TodoController(auth.get_access_token())
                added = todo_ctrl.add_multiple_tasks(result["action_items"], meeting_title)
                if added:
                    st.success(f"{len(added)} nalog dodanih v Microsoft To-Do.")
                else:
                    st.warning("Napaka pri dodajanju nalog")

        if result.get("onenote_page") and result["onenote_page"].get("url"):
            st.markdown('<div class="section-title">Shranjeno v OneNote</div>', unsafe_allow_html=True)
            st.link_button("Odpri v OneNote", result["onenote_page"]["url"], use_container_width=True)


def _extract_text_from_file(uploaded_file):
    """Izlušči tekst iz datoteke"""
    file_type = uploaded_file.type
    file_content = uploaded_file.read()

    try:
        if file_type == "text/plain":
            return file_content.decode("utf-8")

        elif file_type == "text/vtt" or uploaded_file.name.endswith(".vtt"):
            text = file_content.decode("utf-8")
            lines = text.split("\n")
            cleaned = []
            for line in lines:
                line = line.strip()
                if line and not ("-->" in line or line.isdigit() or line.startswith("WEBVTT")):
                    cleaned.append(line)
            return " ".join(cleaned)

        elif "audio" in file_type or uploaded_file.name.endswith(".mp3"):
            return "MP3 obdelava zahteva Azure Speech Services ali Whisper API. Zaenkrat podpiramo samo .txt in .vtt."

        else:
            return file_content.decode("utf-8", errors="ignore")

    except Exception as e:
        st.error(f"Napaka pri branju datoteke: {str(e)}")
        return None