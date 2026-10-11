# views/components/sidebar.py
import streamlit as st
from router import router
from controllers.auth_controller import AuthController


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
    # Profil uporabnika
    # ------------------------------------------------------------------
    display_name = (user_info or {}).get("displayName", "Uporabnik")
    email = (user_info or {}).get("mail", (user_info or {}).get("userPrincipalName", ""))
    initials = "".join([p[0] for p in display_name.split()[:2]]).upper() or "U"

    st.markdown(
        f"""
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{initials}</div>
            <div>
                <div class="sidebar-name">{display_name}</div>
                <div class="sidebar-email">{email}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Navigacija
    # ------------------------------------------------------------------
    current_path = router.get_current_path()

    nav_items = {
        "dashboard": {"label": "📊  Dashboard", "path": "/dashboard"},
        "meetings": {"label": "📅  Moji sestanki", "path": "/meetings"},
        "smart_meeting": {"label": "✨  Pametni sestanek", "path": "/smart-meeting"},
        "email_meetings": {"label": "✉️  E-pošta → sestanek", "path": "/email-meetings"},
        "upload": {"label": "📁  Upload zapisnika", "path": "/upload"},
        "summaries": {"label": "🤖  AI povzetki", "path": "/summaries"},
        "tasks": {"label": "✅  Moje naloge", "path": "/tasks"},
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
    # Rdeča barva gumba je v CSS (.st-key-logout_btn)
    if st.button("🚪  Odjava", key="logout_btn", use_container_width=True):
        auth.logout()
        router.navigate_to("/")

    st.markdown('<div class="sidebar-footer">Meeting Assistant v2.0</div>', unsafe_allow_html=True)
