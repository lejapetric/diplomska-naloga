# controllers/auth_controller.py
import streamlit as st
import requests
import urllib.parse
from config.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL, SCOPES
from services.microsoft_graph_service import MicrosoftGraphService

class AuthController:
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        if "access_token" not in st.session_state:
            st.session_state.access_token = None
        if "user_info" not in st.session_state:
            st.session_state.user_info = None
        if "auth_processed" not in st.session_state:
            st.session_state.auth_processed = False
        if "refresh_token" not in st.session_state:
            st.session_state.refresh_token = None
        if "sidebar_open" not in st.session_state:
            st.session_state.sidebar_open = True
    
    def is_authenticated(self):
        return st.session_state.access_token is not None
    
    def get_user_info(self):
        return st.session_state.user_info
    
    def get_access_token(self):
        return st.session_state.access_token
    
    def get_refresh_token(self):
        return st.session_state.refresh_token
    
    def check_auth_callback(self):
        """Preveri URL za authorization code"""
        query_params = st.query_params
        
        if "code" in query_params and not st.session_state.access_token and not st.session_state.auth_processed:
            st.session_state.auth_processed = True
            auth_code = query_params["code"]
            st.query_params.clear()
            self._exchange_code_for_token(auth_code)
            return True
        
        if "error" in query_params:
            st.error(f"Napaka pri prijavi: {query_params.get('error_description', 'Neznana napaka')}")
            st.query_params.clear()
            return False
        
        return False
    
    def _exchange_code_for_token(self, auth_code):
        """Zamenja kodo za token"""
        if not CLIENT_ID or not CLIENT_SECRET:
            st.error("Microsoft 365 integracija ni nastavljena. Preverite .env datoteko.")
            return
        
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "scope": " ".join(SCOPES)
        }
        
        try:
            response = requests.post(TOKEN_URL, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                st.session_state.access_token = token_data["access_token"]
                st.session_state.refresh_token = token_data.get("refresh_token")
                self._fetch_user_info()
                st.success("✅ Uspešno prijavljeni!")
                st.query_params.clear()
                st.rerun()
            else:
                error_msg = f"Napaka pri prijavi: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error_description" in error_data:
                        error_msg += f" - {error_data['error_description']}"
                except:
                    pass
                st.error(error_msg)
                st.session_state.auth_processed = False
                
        except Exception as e:
            st.error(f"Napaka pri povezavi: {str(e)}")
            st.session_state.auth_processed = False
    
    def _fetch_user_info(self):
        """Pridobi podatke o uporabniku"""
        graph_service = MicrosoftGraphService(st.session_state.access_token)
        user_info = graph_service.get_user_info()
        
        if user_info:
            st.session_state.user_info = user_info
    
    def get_login_url(self):
        """Vrne URL za Microsoft prijavo"""
        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": " ".join(SCOPES),
            "response_mode": "query",
            "prompt": "select_account"
        }
        return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    def logout(self):
        """Odjavi uporabnika"""
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.session_state.auth_processed = False
        st.session_state.refresh_token = None
        st.query_params.clear()