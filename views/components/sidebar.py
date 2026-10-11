# views/components/sidebar.py
import streamlit as st
from router import router
from controllers.auth_controller import AuthController


def show_sidebar(is_authenticated, user_info):
    """Prikaže sidebar z navigacijo - vedno se izriše."""
    
    # ------------------------------------------------------------------
    # CSS za lepši sidebar
    # ------------------------------------------------------------------
    st.markdown("""
    <style>
    /* Sidebar splošno */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Skrij privzeti Streamlit navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Profil */
    .sidebar-profile {
        text-align: center;
        padding: 0 1rem 1rem;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 1rem;
    }
    .sidebar-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.75rem;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    .sidebar-name {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.95rem;
        margin-bottom: 0.15rem;
        line-height: 1.2;
    }
    .sidebar-email {
        font-size: 0.72rem;
        color: #94a3b8;
        word-break: break-all;
    }
    
    /* Sekcijski naslov */
    .sidebar-section {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        padding: 0.5rem 1rem 0.4rem;
        margin-top: 0.5rem;
    }
    
    /* Gumbi v sidebaru */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.15rem;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        padding: 0.55rem 0.9rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        border: none;
        background: transparent;
        color: #475569;
        transition: all 0.15s ease;
        box-shadow: none;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9;
        color: #1e293b;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #eff6ff;
        color: #2563eb;
        font-weight: 600;
        border-left: 3px solid #2563eb;
        padding-left: calc(0.9rem - 3px);
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #dbeafe;
    }
    
    /* Logout gumb */
    .logout-container [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .logout-btn .stButton > button {
        color: #dc2626 !important;
        border: 1px solid #fee2e2 !important;
        background: #fef2f2 !important;
    }
    [data-testid="stSidebar"] .logout-btn .stButton > button:hover {
        background: #fee2e2 !important;
        color: #b91c1c !important;
    }
    
    /* Footer z verzijo */
    .sidebar-footer {
        font-size: 0.7rem;
        color: #cbd5e1;
        text-align: center;
        padding: 0.75rem 1rem 0;
        border-top: 1px solid #f1f5f9;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ------------------------------------------------------------------
    # Če uporabnik NI prijavljen
    # ------------------------------------------------------------------
    if not is_authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔌</div>
            <div style="font-weight: 600; color: #1e293b; font-size: 1rem; margin-bottom: 0.35rem;">
                Niste prijavljeni
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
                Prijavite se z Microsoft 365 za dostop do vseh funkcij.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # ------------------------------------------------------------------
    # Profil uporabnika
    # ------------------------------------------------------------------
    display_name = (user_info or {}).get('displayName', 'Uporabnik')
    email = (user_info or {}).get('mail', (user_info or {}).get('userPrincipalName', ''))
    initials = ''.join([p[0] for p in display_name.split()[:2]]).upper() or "U"
    
    st.markdown(f"""
    <div class="sidebar-profile">
        <div class="sidebar-avatar">{initials}</div>
        <div class="sidebar-name">{display_name}</div>
        <div class="sidebar-email">{email}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ------------------------------------------------------------------
    # Navigacija
    # ------------------------------------------------------------------
    st.markdown('<div class="sidebar-section">Navigacija</div>', unsafe_allow_html=True)
    
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
        is_active = current_path == item["path"]
        button_type = "primary" if is_active else "secondary"
        
        if st.button(
            item["label"],
            key=f"nav_{key}",
            use_container_width=True,
            type=button_type,
        ):
            router.navigate_to(item["path"])
    
    # ------------------------------------------------------------------
    # Potisni logout na dno
    # ------------------------------------------------------------------
    st.markdown('<div style="flex: 1 1 auto; min-height: 2rem;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">Račun</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    auth = AuthController()
    if st.button("🚪  Odjava", key="logout_btn", use_container_width=True, type="secondary"):
        auth.logout()
        router.navigate_to("/")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="sidebar-footer">Meeting Assistant · v1.0</div>',
        unsafe_allow_html=True,
    )