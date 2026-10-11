# views/pages/user_info.py
import streamlit as st
from controllers.auth_controller import AuthController


def show_user_info():
    """Prikaže podatke o prijavljenem uporabniku."""
    auth = AuthController()
    user_info = auth.get_user_info() or {}

    display_name = user_info.get("displayName", "Uporabnik")
    email = user_info.get("mail", user_info.get("userPrincipalName", ""))
    initials = "".join([p[0] for p in display_name.split()[:2]]).upper() or "U"

    st.markdown(
        f"""
        <div class="user-info-header" style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
            <div class="sidebar-avatar" style="width:64px;height:64px;font-size:1.4rem;">{initials}</div>
            <div>
                <h2 style="margin:0;">{display_name}</h2>
                <div class="meta">{email}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="header-rule"></div>', unsafe_allow_html=True)

    st.markdown("### Podatki o uporabniku")
    for key, value in user_info.items():
        if value:
            st.markdown(
                f"""
                <div class="detail-box" style="margin-bottom:0.5rem;">
                    <strong>{key}:</strong> {value}
                </div>
                """,
                unsafe_allow_html=True,
            )