# views/pages/summaries_page.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.onenote_controller import OneNoteController
from router import router
from utils.helpers import format_datetime


def show_summaries_page():
    auth = AuthController()

    if not auth.is_authenticated():
        st.warning("Za ogled povzetkov se morate prijaviti")
        return

    head, btn = st.columns([5, 1])
    with head:
        st.title("AI povzetki")
        st.caption("Povzetki sestankov, shranjeni v OneNote")
    with btn:
        st.write("")
        if st.button("Osveži", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    onenote_ctrl = OneNoteController(auth.get_access_token())

    with st.spinner("Nalaganje povzetkov iz OneNote..."):
        summaries = onenote_ctrl.get_all_summaries()

    if not summaries:
        st.markdown(
            '<div class="empty-state">Ni povzetkov. Naložite zapisnik sestanka in AI jih bo pripravil.</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Naloži prvi zapisnik", type="primary"):
            router.navigate_to("/upload")
        return

    st.markdown(
        f'<div class="section-title">{len(summaries)} povzetkov</div>',
        unsafe_allow_html=True,
    )

    for summary in summaries:
        title = summary.get("title", "Brez naslova")
        created_at = summary.get("created_at", "")
        web_url = summary.get("web_url")

        with st.container(border=True):
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                meta = f"Ustvarjeno: {format_datetime(created_at)}" if created_at else ""
                st.markdown(
                    f'<div class="row-title">{title}</div><div class="row-meta">{meta}</div>',
                    unsafe_allow_html=True,
                )
            with col_btn:
                if web_url:
                    st.link_button("Odpri", web_url, use_container_width=True)