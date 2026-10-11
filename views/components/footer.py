# views/components/footer.py
import streamlit as st
from datetime import datetime

def show_footer():
    """Prikaže footer fiksiran na dnu - vidi se šele ko skrolaš čisto dol"""
    
    current_year = datetime.now().year
    
    st.markdown("""
    <style>
    /* Skrij Streamlitov privzeti footer in header */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Dodaj padding na dno vsebine, da footer ne prekrije vsebine */
    .main .block-container {
        padding-bottom: 320px !important;
    }
    
    /* Fiksiran footer na dnu viewporta */
    .app-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #e2e8f0;
        padding: 1.5rem 0 0.75rem;
        z-index: 999;
    }
    .footer-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        margin-bottom: 1.5rem;
    }
    .footer-section h4 {
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .footer-section ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .footer-section li {
        margin-bottom: 0.4rem;
    }
    .footer-section a {
        color: #64748b;
        text-decoration: none;
        font-size: 0.875rem;
    }
    .footer-section a:hover {
        color: #2563eb;
    }
    .footer-bottom {
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
        text-align: center;
        font-size: 0.75rem;
        color: #94a3b8;
    }
    .footer-bottom a {
        color: #94a3b8;
        text-decoration: none;
        margin: 0 0.5rem;
    }
    .footer-bottom a:hover {
        color: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)
    
    footer_html = f'''
    <div class="app-footer">
        <div class="footer-container">
            <div class="footer-grid">
                <div class="footer-section">
                    <h4>📌 Meeting Assistant</h4>
                    <p style="color: #64748b; font-size: 0.875rem;">Avtomatizacija sestankov z AI. Povzetki, naloge in integracija z Microsoft 365.</p>
                </div>
                <div class="footer-section">
                    <h4>☁️ Microsoft 365</h4>
                    <ul>
                        <li>📅 Outlook koledar</li>
                        <li>🎙️ Teams transkripti</li>
                        <li>✅ Microsoft To-Do</li>
                        <li>📓 OneNote shranjevanje</li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>⚡ Funkcionalnosti</h4>
                    <ul>
                        <li>🤖 AI povzetki</li>
                        <li>📋 Samodejne naloge</li>
                        <li>⏰ Pametno načrtovanje</li>
                        <li>📁 Upload zapisnikov</li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>📞 Kontakt</h4>
                    <ul>
                        <li>📧 info@meeting-assistant.si</li>
                        <li>📍 Ljubljana, Slovenija</li>
                        <li>🆘 Podpora</li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <a href="#">Pogoji uporabe</a>
                <span>•</span>
                <a href="#">Varstvo podatkov</a>
                <span>•</span>
                <a href="#">Piškotki</a>
                <span>•</span>
                <a href="#">GDPR</a>
                <br><br>
                © {current_year} Meeting Assistant. Vse pravice pridržane.
                <br>
                <span style="font-size: 0.7rem;">🔒 Varno in zasebno. Vaši podatki ostajajo v Microsoft 365.</span>
            </div>
        </div>
    </div>
    '''
    
    st.markdown(footer_html, unsafe_allow_html=True)