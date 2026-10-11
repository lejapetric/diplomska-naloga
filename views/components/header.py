# views/components/header.py
import streamlit as st
from controllers.auth_controller import AuthController

LOGO_HTML = '<div class="logo-text">Meeting<span>Assistant</span></div>'


def show_header():
    """Prikaže header z logotipom in uporabnikom.
    Ves stil je v static/style.css."""

    auth = AuthController()
    is_authenticated = auth.is_authenticated()
    user_info = auth.get_user_info() if is_authenticated else None

    # ------------------------------------------------------------------
    # Uporabnik NI prijavljen
    # ------------------------------------------------------------------
    if not is_authenticated:
        col1, col2 = st.columns([6, 3])

        with col1:
            st.markdown(LOGO_HTML, unsafe_allow_html=True)

        with col2:
            st.markdown(
                f"""
                <div style="text-align: right;">
                    <a href="{auth.get_login_url()}" target="_self" class="login-btn">Prijava z Microsoft 365</a>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="header-rule"></div>', unsafe_allow_html=True)
        return

    # ------------------------------------------------------------------
    # Uporabnik je PRIJAVLJEN
    # ------------------------------------------------------------------
    sidebar_open = st.session_state.get("sidebar_open", True)

    col1, col2, col3 = st.columns([5, 3, 2])

    with col1:
        # Gumb + logotip se prikažeta v headerju SAMO, ko je sidebar zaprt
        if not sidebar_open:
            toggle_col, logo_col = st.columns([1, 5])

            with toggle_col:
                if st.button("☰", key="open_sidebar_btn"):
                    st.session_state.sidebar_open = True
                    st.rerun()

            with logo_col:
                st.markdown(LOGO_HTML, unsafe_allow_html=True)
        # Ko je sidebar odprt, je col1 prazen (logotip je v sidebaru)

    with col2:
        if user_info:
            display_name = user_info.get("displayName", "Uporabnik")
            email = user_info.get("mail", user_info.get("userPrincipalName", ""))
            st.markdown(
                f"""
                <div class="user-chip">
                    <div class="name">{display_name}</div>
                    <div class="email">{email}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col3:
        if st.button("👤 User info", key="header_user_info_btn"):
            st.session_state.page = "user_info"
            st.rerun()

    st.markdown('<div class="header-rule"></div>', unsafe_allow_html=True)