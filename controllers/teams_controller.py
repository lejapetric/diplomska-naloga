# controllers/teams_controller.py
import requests
from datetime import datetime, timedelta
from services.microsoft_graph_service import MicrosoftGraphService
import streamlit as st

class TeamsController:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.graph_service = MicrosoftGraphService(access_token)
    
    def get_teams_meetings(self, days_back=30):
        """Pridobi Teams sestanke iz koledarja"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Pridobi vse sestanke v časovnem obdobju
        events = self.graph_service.get_calendar_events(limit=100)
        
        # Filtriraj samo Teams sestanke
        teams_meetings = []
        for event in events:
            is_online = event.get("isOnlineMeeting", False)
            has_teams = "Teams" in event.get("subject", "") or "Teams" in event.get("location", {}).get("displayName", "")
            
            if is_online or has_teams:
                teams_meetings.append(event)
        
        return teams_meetings
    
    def get_meeting_transcript(self, meeting_id):
        """Pridobi transkript Teams sestanka (če obstaja)"""
        # To zahteva posebne dovolilnice in je pogosto omejeno
        # Trenutno Graph API ne podpira direktnega branja transkriptov
        # Namesto tega uporabimo OnlineMeeting API
        
        url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings?$filter=JoinWebUrl eq '{meeting_id}'"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                meetings = response.json().get("value", [])
                if meetings:
                    # Pridobi podrobnosti
                    meeting = meetings[0]
                    return {
                        "subject": meeting.get("subject"),
                        "start_time": meeting.get("startDateTime"),
                        "join_url": meeting.get("joinUrl"),
                        "transcript_available": False  # API ne podpira direktnega dostopa
                    }
            
            return None
            
        except Exception as e:
            st.warning(f"Transkript ni na voljo: {str(e)}")
            return None
    
    def get_meeting_recording(self, meeting_id):
        """Pridobi posnetek sestanka"""
        # Posnetki so shranjeni v SharePoint/OneDrive
        # To zahteva dodatne dovolilnice
        return None
    
    def process_teams_meeting(self, meeting):
        """Obdela Teams sestanek in vrne podatke za AI"""
        meeting_id = meeting.get("id")
        subject = meeting.get("subject", "Brez naslova")
        
        # Poskusi pridobiti transkript
        transcript_data = self.get_meeting_transcript(meeting_id)
        
        # Če transkript ni na voljo, vrni opozorilo
        return {
            "id": meeting_id,
            "subject": subject,
            "start_time": meeting.get("start", {}).get("dateTime"),
            "has_transcript": transcript_data is not None and transcript_data.get("transcript_available", False),
            "join_url": meeting.get("onlineMeeting", {}).get("joinUrl", ""),
            "message": "Transkript ni na voljo preko Graph API. Poskusite ročno uploadati zapisnik."
        }