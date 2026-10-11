# services/microsoft_graph_service.py
import requests
from datetime import datetime, timedelta
import streamlit as st

class MicrosoftGraphService:
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
    
    def set_token(self, token):
        self.access_token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def _make_request(self, method, url, **kwargs):
        """Pomožna funkcija za API klic"""
        headers = kwargs.pop('headers', {})
        headers.update(self.headers)
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            return response
        except Exception as e:
            st.error(f"API napaka: {str(e)}")
            return None
    
    def get_user_info(self):
        """Pridobi podatke o uporabniku"""
        if not self.access_token:
            return None
        
        response = self._make_request("GET", "https://graph.microsoft.com/v1.0/me")
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_calendar_events(self, limit=50):
        """Pridobi sestanke iz koledarja"""
        if not self.access_token:
            return []
        
        url = f"https://graph.microsoft.com/v1.0/me/events?$top={limit}&$orderby=start/dateTime"
        response = self._make_request("GET", url)
        
        if response and response.status_code == 200:
            return response.json().get("value", [])
        return []
    
    def get_event_details(self, event_id):
        """Pridobi podrobnosti sestanka"""
        if not self.access_token:
            return None
        
        url = f"https://graph.microsoft.com/v1.0/me/events/{event_id}"
        response = self._make_request("GET", url)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def create_event(self, subject, start_time, end_time, attendees, location="", body=""):
        """Ustvari nov sestanek"""
        if not self.access_token:
            return None
        
        attendee_list = [
            {"emailAddress": {"address": email}, "type": "required"} 
            for email in attendees if email
        ]
        
        event = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body},
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Central European Standard Time"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Central European Standard Time"},
            "location": {"displayName": location or "Microsoft Teams"},
            "attendees": attendee_list,
            "allowNewTimeProposals": True
        }
        
        # Dodaj Teams povezavo
        if "Teams" in location or not location:
            event["isOnlineMeeting"] = True
            event["onlineMeetingProvider"] = "teamsForBusiness"
        
        response = self._make_request("POST", "https://graph.microsoft.com/v1.0/me/events", json=event)
        
        if response and response.status_code == 201:
            return response.json()
        return None
    
    def get_free_busy(self, emails, start_date, end_date):
        """Preveri prosti čas udeležencev"""
        if not self.access_token:
            return None
        
        body = {
            "schedules": emails,
            "startTime": {
                "dateTime": start_date.isoformat(),
                "timeZone": "Central European Standard Time"
            },
            "endTime": {
                "dateTime": end_date.isoformat(),
                "timeZone": "Central European Standard Time"
            },
            "availabilityViewInterval": 30
        }
        
        response = self._make_request(
            "POST",
            "https://graph.microsoft.com/v1.0/me/calendar/getSchedule",
            json=body
        )
        
        if response and response.status_code == 200:
            return response.json().get("value", [])
        return None
    
    def get_todo_lists(self):
        """Pridobi To-Do liste"""
        if not self.access_token:
            return []
        
        response = self._make_request("GET", "https://graph.microsoft.com/v1.0/me/todo/lists")
        
        if response and response.status_code == 200:
            return response.json().get("value", [])
        return []
    
    def create_todo_task(self, list_id, title, details="", due_date=None):
        """Ustvari nalogo v To-Do"""
        if not self.access_token:
            return None
        
        task = {
            "title": title,
            "body": {"content": details, "contentType": "text"},
            "importance": "normal",
            "status": "notStarted"
        }
        
        if due_date and due_date != "TBD":
            task["dueDateTime"] = {
                "dateTime": due_date,
                "timeZone": "Central European Standard Time"
            }
        
        url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks"
        response = self._make_request("POST", url, json=task)
        
        if response and response.status_code == 201:
            return response.json()
        return None
    
    def get_calendar_events_cached(self, limit=50):
        """Cacheana verzija za koledar"""
        return self.get_calendar_events(limit)
    
    def get_todo_lists_cached(self):
        """Cacheana verzija za To-Do liste"""
        return self.get_todo_lists()