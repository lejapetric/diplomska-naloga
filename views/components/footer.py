import streamlit as st

def show_footer():
    st.markdown(
        """
        <div class="app-footer">
            <div class="footer-brand">Meeting Assistant</div>
            <div class="footer-group">
                <a href="#">Pomoč</a>
                <a href="#">Zasebnost</a>
                <a href="#">Kontakt</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )