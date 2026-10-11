# views/pages/hero.py
import streamlit as st


def show_hero():
    """Prikaže hero za neprijavljene uporabnike. Stil je v static/style.css."""

    st.markdown(
        """
        <div class="hero">
            <h1 class="hero-title">Pametnejši sestanki z AI</h1>
            <p class="hero-description">
                Avtomatizirajte povzetke, naloge in zapisnike s pomočjo umetne inteligence
                in brezhibne integracije z Microsoft 365.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

