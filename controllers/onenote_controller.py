# controllers/onenote_controller.py
import requests
from datetime import datetime
from services.microsoft_graph_service import MicrosoftGraphService
import streamlit as st

class OneNoteController:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def get_or_create_notebook(self, notebook_name="Meeting Assistant"):
        """Poišče ali ustvari zvezek v OneNote"""
        url = "https://graph.microsoft.com/v1.0/me/onenote/notebooks"
        
        try:
            # Poišči obstoječe zvezke
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                notebooks = response.json().get("value", [])
                for notebook in notebooks:
                    if notebook.get("displayName") == notebook_name:
                        return notebook.get("id")
            
            # Ustvari nov zvezek
            data = {"displayName": notebook_name}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                return response.json().get("id")
            
            return None
            
        except Exception as e:
            st.error(f"Napaka pri dostopu do OneNote: {str(e)}")
            return None
    
    def get_or_create_section(self, notebook_id, section_name):
        """Poišče ali ustvari section v zvezku"""
        url = f"https://graph.microsoft.com/v1.0/me/onenote/notebooks/{notebook_id}/sections"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                sections = response.json().get("value", [])
                for section in sections:
                    if section.get("displayName") == section_name:
                        return section.get("id")
            
            # Ustvari nov section
            data = {"displayName": section_name}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                return response.json().get("id")
            
            return None
            
        except Exception as e:
            st.error(f"Napaka pri dostopu do sectiona: {str(e)}")
            return None
    
    def save_meeting_summary(self, meeting_title, summary, action_items, meeting_date, attendees):
        """Shrani povzetek sestanka v OneNote"""
        notebook_id = self.get_or_create_notebook()
        if not notebook_id:
            st.error("Napaka pri ustvarjanju OneNote zvezka")
            return None
        
        # Ustvari section za tekoče leto
        current_year = datetime.now().strftime("%Y")
        section_id = self.get_or_create_section(notebook_id, current_year)
        
        if not section_id:
            st.error("Napaka pri ustvarjanju sectiona")
            return None
        
        # Oblikuj HTML vsebino
        attendees_html = ""
        if attendees:
            attendees_html = "<ul>"
            for attendee in attendees:
                attendees_html += f"<li>{attendee}</li>"
            attendees_html += "</ul>"
        
        # Oblikuj naloge
        tasks_html = ""
        if action_items:
            tasks_html = "<ul>"
            for item in action_items:
                if isinstance(item, dict):
                    task = item.get("task", "")
                    assignee = item.get("assignee", "TBD")
                    due_date = item.get("due_date", "TBD")
                    tasks_html += f"<li><strong>{task}</strong><br>Odgovoren: {assignee}<br>Rok: {due_date}</li>"
                else:
                    tasks_html += f"<li>{item}</li>"
            tasks_html += "</ul>"
        else:
            tasks_html = "<p>Ni izluščenih nalog.</p>"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{meeting_title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e293b; margin-top: 25px; }}
        .metadata {{ background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .summary {{ background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #2563eb; margin: 20px 0; }}
        .tasks {{ background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #64748b; margin-top: 40px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 20px; }}
    </style>
</head>
<body>
    <h1>📅 {meeting_title}</h1>
    
    <div class="metadata">
        <p><strong>📆 Datum:</strong> {meeting_date}</p>
        <p><strong>👥 Udeleženci:</strong></p>
        {attendees_html}
    </div>
    
    <div class="summary">
        <h2>📝 AI Povzetek</h2>
        <p>{summary}</p>
    </div>
    
    <div class="tasks">
        <h2>✅ Naloge iz sestanka</h2>
        {tasks_html}
    </div>
    
    <div class="footer">
        <p>Generirano z Meeting Assistant AI • {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
    </div>
</body>
</html>"""
        
        # Ustvari stran v sectionu
        page_url = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages"
        page_headers = {
            **self.headers,
            "Content-Type": "application/xhtml+xml"
        }
        
        try:
            response = requests.post(page_url, headers=page_headers, data=html_content.encode('utf-8'))
            
            if response.status_code == 201:
                page_data = response.json()
                return {
                    "id": page_data.get("id"),
                    "title": page_data.get("title"),
                    "url": page_data.get("links", {}).get("oneNoteWebUrl", {}).get("href")
                }
            else:
                st.error(f"Napaka pri shranjevanju v OneNote: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Napaka pri povezavi z OneNote: {str(e)}")
            return None
    
    def get_all_summaries(self, limit=50):
        """Pridobi vse povzetke iz OneNote"""
        notebook_id = self.get_or_create_notebook()
        if not notebook_id:
            return []
        
        # Pridobi vse strani iz vseh sectionov
        url = f"https://graph.microsoft.com/v1.0/me/onenote/notebooks/{notebook_id}/pages?$top={limit}&$orderby=createdDateTime desc"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                pages = response.json().get("value", [])
                summaries = []
                
                for page in pages:
                    summaries.append({
                        "id": page.get("id"),
                        "title": page.get("title"),
                        "created_at": page.get("createdDateTime"),
                        "web_url": page.get("links", {}).get("oneNoteWebUrl", {}).get("href"),
                        "client_url": page.get("links", {}).get("oneNoteClientUrl", {}).get("href")
                    })
                
                return summaries
            
            return []
            
        except Exception as e:
            st.error(f"Napaka pri nalaganju povzetkov: {str(e)}")
            return []
    
    def get_page_content(self, page_id):
        """Pridobi vsebino strani"""
        url = f"https://graph.microsoft.com/v1.0/me/onenote/pages/{page_id}/content"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.text
            return None
            
        except Exception as e:
            st.error(f"Napaka pri nalaganju vsebine: {str(e)}")
            return None