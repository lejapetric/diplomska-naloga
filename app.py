# app.py
import streamlit as st
from config.settings import APP_NAME
from controllers.auth_controller import AuthController
from views import show_hero, show_dashboard, show_meetings_page, show_smart_meeting_page
from views import show_email_meetings_page, show_upload_page, show_summaries_page, show_tasks_page
from views.components import show_header, show_sidebar, show_footer
from router import router

# ------------------------------------------------------------------
# Konfiguracija strani (MORA biti prvi Streamlit ukaz!)
# ------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------
# Naloži CSS
# ------------------------------------------------------------------
def load_css():
    try:
        with open("static/style.css", "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
        .stAppDeployButton, .stToolbar, .stMainBlockHeader,
        [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"] { display: none !important; }
        .main .block-container { padding-top: 0 !important; }
        </style>
        """, unsafe_allow_html=True)

load_css()

# ------------------------------------------------------------------
# Inicializacija routerja
# ------------------------------------------------------------------
if "router_current_path" not in st.session_state:
    st.session_state.router_current_path = "/"

# ------------------------------------------------------------------
# Inicializacija auth controllerja
# ------------------------------------------------------------------
auth = AuthController()

# Preveri OAuth callback
if not auth.is_authenticated():
    auth.check_auth_callback()

# Session state za sidebar
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

# ------------------------------------------------------------------
# Glavna vsebina
# ------------------------------------------------------------------
is_authenticated = auth.is_authenticated()
user_info = auth.get_user_info() if is_authenticated else None

# Header (vedno prikazan)
show_header()

# Sidebar - prikaži samo, ko je uporabnik prijavljen
if is_authenticated:
    with st.sidebar:
        show_sidebar(is_authenticated, user_info)

# Glavna vsebina - routing
if not is_authenticated:
    show_hero()
else:
    current_path = router.get_current_path()
    
    page_map = {
        "/": show_dashboard,
        "/dashboard": show_dashboard,
        "/meetings": show_meetings_page,
        "/smart-meeting": show_smart_meeting_page,
        "/email-meetings": show_email_meetings_page,
        "/upload": show_upload_page,
        "/summaries": show_summaries_page,
        "/tasks": show_tasks_page
    }
    
    page_function = page_map.get(current_path, show_dashboard)
    page_function()

# Footer
show_footer()