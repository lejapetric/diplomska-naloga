# views/components/footer.py
import streamlit as st
from datetime import datetime


def show_footer():
    """Minimalen footer na koncu vsebine. Stil je v static/style.css."""

    current_year = datetime.now().year

    st.markdown(
        f"""
        <div class="app-footer">
            <div class="footer-group">
                <span class="footer-brand">Meeting Assistant</span>
                <span>© {current_year}</span>
                <span>Ljubljana, Slovenija</span>
            </div>
            <div class="footer-group">
                <a href="#">Pogoji uporabe</a>
                <a href="#">Varstvo podatkov</a>
                <a href="#">Piškotki</a>
                <a href="mailto:info@meeting-assistant.si">Kontakt</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
