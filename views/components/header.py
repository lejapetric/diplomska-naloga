# views/components/header.py
import streamlit as st
from router import router
from controllers.auth_controller import AuthController


def show_header():
    """Prikaže header z logotipom, menijem in gumbom za sidebar"""
    
    auth = AuthController()
    is_authenticated = auth.is_authenticated()
    user_info = auth.get_user_info() if is_authenticated else None
    
    st.markdown("""
    <style>
    .app-header {
        background: white;
        border-bottom: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        margin-bottom: 1.5rem;
        margin-top: 0;
        width: 100%;
    }
    .header-container {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    .logo {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
    }
    .logo-text {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
    }
    .logo-text span {
        color: #2563eb;
    }
    .login-btn {
        background: #2563eb;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        white-space: nowrap;
    }
    .login-btn:hover {
        background: #1d4ed8;
        color: white;
        text-decoration: none;
    }
    </style>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    # ------------------------------------------------------------------
    # Če uporabnik NI prijavljen
    # ------------------------------------------------------------------
    if not is_authenticated:
        col1, col2, col3 = st.columns([1, 6, 3])
        
        with col1:
            st.write("")
        
        with col2:
            st.markdown("""
            <div class="logo" style="display: inline-flex; cursor: pointer; align-items: center; height: 40px;" onclick="window.location.href='?page='">
                <div class="logo-text">Meeting<span>Assistant</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            login_url = auth.get_login_url()
            st.markdown(f"""
            <div style="text-align: right;">
                <a href="{login_url}" target="_self" class="login-btn">🔌 Prijava z Microsoft 365</a>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # ------------------------------------------------------------------
    # Uporabnik je PRIJAVLJEN
    # ------------------------------------------------------------------
    col1, col2, col3 = st.columns([1, 6, 3])
    
    with col1:
        # Gumb za toggle sidebar
        if st.button("✕" if st.session_state.get("sidebar_open", True) else "☰", key="toggle_sidebar_btn"):
            st.session_state.sidebar_open = not st.session_state.get("sidebar_open", True)
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="logo" style="display: inline-flex; cursor: pointer; align-items: center; height: 40px;" onclick="window.location.href='?page=dashboard'">
            <div class="logo-text">Meeting<span>Assistant</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if user_info:
            display_name = user_info.get('displayName', 'Uporabnik')
            email = user_info.get('mail', user_info.get('userPrincipalName', ''))
            st.markdown(f"""
            <div style="text-align: right;">
                <div style="font-weight: 600; color: #1e293b;">👤 {display_name}</div>
                <div style="font-size: 0.7rem; color: #64748b;">{email}</div>
            </div>
            """, unsafe_allow_html=True)