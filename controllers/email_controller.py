# controllers/email_controller.py
import requests
from services.microsoft_graph_service import MicrosoftGraphService
from services.email_analyzer_service import EmailAnalyzerService
import streamlit as st

class EmailController:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.email_analyzer = EmailAnalyzerService()
        self.graph_service = MicrosoftGraphService(access_token)
    
    def get_recent_emails(self, limit=20):
        """Pridobi zadnje e-pošte"""
        url = f"https://graph.microsoft.com/v1.0/me/messages?$top={limit}&$orderby=receivedDateTime desc&$select=id,subject,from,receivedDateTime,bodyPreview"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("value", [])
            return []
        except Exception as e:
            st.error(f"Napaka pri branju e-pošte: {str(e)}")
            return []
    
    def find_meeting_requests(self, limit=20):
        """Poišče e-pošte, ki vsebujejo zahteve za sestanek"""
        emails = self.get_recent_emails(limit)
        meeting_requests = []
        
        for email in emails:
            subject = email.get("subject", "")
            sender = email.get("from", {}).get("emailAddress", {}).get("address", "")
            received = email.get("receivedDateTime", "")
            body_preview = email.get("bodyPreview", "")
            
            # Analiziraj e-pošto
            analysis = self.email_analyzer.analyze_email(subject, body_preview, sender)
            
            if analysis:
                analysis["email_id"] = email.get("id")
                analysis["received_date"] = received
                meeting_requests.append(analysis)
        
        return meeting_requests
    
    def create_meeting_from_email(self, request, user_email):
        """Ustvari sestanek iz zahteve e-pošte"""
        try:
            title = request.get("meeting_title", "Sestanek iz e-pošte")
            start_date = request.get("suggested_date")
            
            if not start_date:
                from datetime import datetime, timedelta
                start_date = datetime.now() + timedelta(days=1)
                if start_date.weekday() >= 5:
                    start_date = start_date + timedelta(days=7 - start_date.weekday())
                start_date = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
            
            # Če je ura predlagana, jo nastavimo
            suggested_time = request.get("suggested_time")
            if suggested_time:
                try:
                    start_date = start_date.replace(hour=suggested_time[0], minute=suggested_time[1])
                except:
                    pass
            
            duration = request.get("suggested_duration", 60)
            end_date = start_date + timedelta(minutes=duration)
            
            attendees = request.get("additional_attendees", [])
            if user_email and user_email not in attendees:
                attendees.append(user_email)
            
            # Ustvari sestanek
            event = self.graph_service.create_event(
                subject=title,
                start_time=start_date,
                end_time=end_date,
                attendees=attendees,
                location=request.get("suggested_location", "Microsoft Teams"),
                body=f"Avtomatsko ustvarjen iz e-pošte.\n\nOriginalno sporočilo:\n{request.get('original_body', '')}"
            )
            
            if event:
                return {
                    "success": True,
                    "title": title,
                    "date": start_date,
                    "attendees": attendees,
                    "event": event
                }
            else:
                return {"success": False, "error": "Napaka pri ustvarjanju sestanka"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _mark_email_as_read(self, email_id):
        """Označi e-pošto kot prebrano"""
        if not email_id:
            return
        
        url = f"https://graph.microsoft.com/v1.0/me/messages/{email_id}"
        data = {"isRead": True}
        
        try:
            requests.patch(url, headers=self.headers, json=data)
        except Exception as e:
            print(f"Napaka pri označevanju e-pošte: {e}")