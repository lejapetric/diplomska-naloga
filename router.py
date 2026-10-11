# router.py
import streamlit as st
from urllib.parse import urlparse, parse_qs

class Router:
    """Simple router for Streamlit with URL paths"""
    
    def __init__(self):
        self.routes = {}
        self._init_session_state()
    
    def _init_session_state(self):
        """Inicializira session_state za router"""
        if "router_current_path" not in st.session_state:
            st.session_state.router_current_path = "/"
        if "router_initialized" not in st.session_state:
            st.session_state.router_initialized = True
    
    def add_route(self, path, handler, name=None):
        """Register a route with a handler function"""
        self.routes[path] = {
            "handler": handler,
            "name": name or path.strip("/") or "home"
        }
    
    def get_current_path(self):
        """Get current path from query params or session state"""
        # Preveri, ali je session_state inicializiran
        if "router_current_path" not in st.session_state:
            self._init_session_state()
        
        # Preveri query params
        query_params = st.query_params
        
        if "page" in query_params and query_params["page"]:
            path = query_params["page"]
            if not path.startswith("/"):
                path = f"/{path}"
            # Shrani v session state
            st.session_state.router_current_path = path
            return path
        
        # Vrni iz session state
        return st.session_state.router_current_path
    
    def navigate_to(self, path, params=None):
        """Navigate to a specific path"""
        if params is None:
            params = {}
        
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"
        
        # Clear existing query params
        st.query_params.clear()
        
        # Set new page param
        page_param = path.lstrip("/")
        if page_param:
            st.query_params["page"] = page_param
        
        # Add additional params
        for key, value in params.items():
            st.query_params[key] = str(value)
        
        # Shrani v session state
        st.session_state.router_current_path = path
        st.rerun()
    
    def handle_request(self):
        """Handle current request and render appropriate page"""
        path = self.get_current_path()
        
        # Find matching route
        if path in self.routes:
            handler = self.routes[path]["handler"]
            handler()
        else:
            # 404 - Page not found
            self._show_404(path)
    
    def _show_404(self, path):
        """Show 404 page"""
        st.error(f"❌ Stran '{path}' ne obstaja")
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem;">
            <h1>404</h1>
            <p>Stran, ki jo iščete, ne obstaja.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 Domača stran"):
            self.navigate_to("/")
    
    def get_url(self, path, params=None):
        """Generate URL for a path"""
        if params is None:
            params = {}
        
        params["page"] = path.lstrip("/")
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        return f"?{query_string}" if query_string else "?"


# Create global router instance
router = Router()