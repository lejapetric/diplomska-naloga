# views/pages/hero.py
import streamlit as st

def show_hero():
    """Prikaže hero page za neprijavljene uporabnike"""
    
    st.markdown("""
    <style>
    /* Hero kontejner */
    .hero-container {
        min-height: 60vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: #ffffff;
    }
    .hero-content {
        text-align: center;
        max-width: 800px;
        width: 100%;
    }
    
    /* Značka */
    .hero-badge {
        margin-bottom: 1.5rem;
    }
    .hero-badge span {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid #dbeafe;
    }
    
    /* Naslov - ČRNA */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #0f172a !important;
        margin-bottom: 1rem;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    
    /* Poudarek - MODRA */
    .hero-highlight {
        color: #2563eb !important;
        -webkit-text-fill-color: #2563eb !important;
        background: none !important;
    }
    
    /* Podnaslov - SIVA */
    .hero-description {
        font-size: 1.2rem;
        color: #475569 !important;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.25rem; }
        .hero-description { font-size: 1rem; }
    }
    </style>
    
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-badge">
                <span>✨ AI-powered asistent</span>
            </div>
            <h1 class="hero-title">
                Pametnejši<br>
                <span class="hero-highlight">sestanki</span> z AI
            </h1>
            <p class="hero-description">
                Avtomatizirajte povzetke, naloge in zapisnike s pomočjo umetne inteligence
                in brezhibne integracije z Microsoft 365.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")