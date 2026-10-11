# views/components/sidebar.py
import streamlit as st
from router import router
from controllers.auth_controller import AuthController
from views.components.header import LOGO_HTML


def show_sidebar(is_authenticated, user_info):
    """Prikaže sidebar z navigacijo. Ves stil je v static/style.css."""

    # ------------------------------------------------------------------
    # Uporabnik NI prijavljen
    # ------------------------------------------------------------------
    if not is_authenticated:
        st.markdown(
            """
            <div class="sidebar-empty">
                <strong>Niste prijavljeni</strong>
                Prijavite se z Microsoft 365 za dostop do vseh funkcij.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ------------------------------------------------------------------
    # Logotip + gumb za zapiranje – čisto na vrhu sidebarja
    # ------------------------------------------------------------------
    logo_col, close_col = st.columns([5, 1], gap="small")

    with logo_col:
        st.markdown(
            f'<div class="sidebar-logo">{LOGO_HTML}</div>',
            unsafe_allow_html=True,
        )

    with close_col:
        if st.button("✕", key="close_sidebar_btn"):
            st.session_state.sidebar_open = False
            st.rerun()

    # ------------------------------------------------------------------
    # Navigacija
    # ------------------------------------------------------------------
    current_path = router.get_current_path()

    nav_items = {
        "dashboard": {"label": "Dashboard", "path": "/dashboard"},
        "meetings": {"label": "Moji sestanki", "path": "/meetings"},
        "smart_meeting": {"label": "Pametni sestanek", "path": "/smart-meeting"},
        "email_meetings": {"label": "E-pošta → sestanek", "path": "/email-meetings"},
        "upload": {"label": "Upload zapisnika", "path": "/upload"},
        "summaries": {"label": "AI povzetki", "path": "/summaries"},
        "tasks": {"label": "Moje naloge", "path": "/tasks"},
    }

    for key, item in nav_items.items():
        is_active = current_path == item["path"] or (current_path == "/" and key == "dashboard")

        if st.button(
            item["label"],
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            router.navigate_to(item["path"])

    # ------------------------------------------------------------------
    # Račun
    # ------------------------------------------------------------------
    st.markdown('<div class="sidebar-section">Račun</div>', unsafe_allow_html=True)

    auth = AuthController()
    if st.button("Odjava", key="logout_btn", use_container_width=True):
        auth.logout()
        router.navigate_to("/")

    st.markdown('<div class="sidebar-footer">Meeting Assistant v2.0</div>', unsafe_allow_html=True)