# services/background_email_service.py
import streamlit as st
from datetime import datetime, timedelta
from controllers.email_controller import EmailController
from controllers.calendar_controller import CalendarController

class BackgroundEmailService:
    """Storitev za samodejno iskanje in ustvarjanje sestankov iz e-pošte"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.email_ctrl = EmailController(access_token)
        self.calendar_ctrl = CalendarController(access_token)
        
        # Inicializiraj pending_meetings v session state, če ne obstaja
        if "pending_meetings" not in st.session_state:
            st.session_state.pending_meetings = []
    
    def find_and_create_pending_meetings(self):
        """Poišče e-pošte z zahtevami za sestanke in ustvari pending sestanke"""
        
        # Poišči zahteve v e-pošti
        meeting_requests = self.email_ctrl.find_meeting_requests(limit=30)
        
        new_pending_meetings = []
        
        for req in meeting_requests:
            # Preveri, ali že obstaja pending sestanek iz te e-pošte
            if not self._is_already_pending(req.get("email_id")):
                # Ustvari pending sestanek (ni še v koledarju)
                pending_meeting = self._create_pending_meeting(req)
                if pending_meeting:
                    new_pending_meetings.append(pending_meeting)
        
        return new_pending_meetings
    
    def _is_already_pending(self, email_id):
        """Preveri, ali že obstaja pending sestanek iz te e-pošte"""
        if not email_id:
            return False
        
        for meeting in st.session_state.pending_meetings:
            if meeting.get("email_id") == email_id:
                return True
        return False
    
    def _create_pending_meeting(self, request):
        """Ustvari pending sestanek (shrani v session state, ne v koledar)"""
        
        # Določi datum
        suggested_date = request.get("suggested_date")
        suggested_time = request.get("suggested_time")
        
        if suggested_date:
            start_date = suggested_date
        else:
            start_date = datetime.now() + timedelta(days=1)
            if start_date.weekday() >= 5:  # Če je vikend
                start_date = start_date + timedelta(days=7 - start_date.weekday())
            start_date = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
        
        if suggested_time:
            try:
                start_date = start_date.replace(hour=suggested_time[0], minute=suggested_time[1])
            except:
                pass
        
        duration = request.get("suggested_duration", 60)
        end_date = start_date + timedelta(minutes=duration)
        
        pending_meeting = {
            "id": f"pending_{datetime.now().timestamp()}_{request.get('email_id', '')}",
            "email_id": request.get("email_id"),
            "title": request.get("meeting_title", "Sestanek iz e-pošte"),
            "sender": request.get("sender", "Neznan"),
            "subject": request.get("subject", ""),
            "start_time": start_date,
            "end_time": end_date,
            "duration": duration,
            "location": request.get("suggested_location", "Microsoft Teams"),
            "attendees": request.get("additional_attendees", []),
            "original_body": request.get("original_body", ""),
            "received_date": request.get("received_date", ""),
            "status": "pending",  # pending, accepted, rejected
            "generated_from_email": True,
            "email_preview": request.get("original_body", "")[:200]
        }
        
        # Shrani v session state
        st.session_state.pending_meetings.append(pending_meeting)
        
        return pending_meeting
    
    def accept_meeting(self, meeting_id):
        """Sprejmi sestanek - ustvari v koledarju"""
        
        # Poišči pending meeting
        pending_meeting = None
        for m in st.session_state.pending_meetings:
            if m.get("id") == meeting_id:
                pending_meeting = m
                break
        
        if not pending_meeting:
            return {"success": False, "error": "Sestanek ni najden"}
        
        # Ustvari sestanek v Outlooku
        attendees = pending_meeting.get("attendees", [])
        user_email = self._get_user_email()
        if user_email and user_email not in attendees:
            attendees.append(user_email)
        
        body = f"""
        <h3>📧 Avtomatsko ustvarjen iz e-pošte</h3>
        <p><strong>Pošiljatelj:</strong> {pending_meeting.get('sender', 'Neznan')}</p>
        <p><strong>Originalni naslov:</strong> {pending_meeting.get('subject', '')}</p>
        
        <hr>
        
        <h4>📝 Originalno sporočilo:</h4>
        <p>{pending_meeting.get('original_body', '')}</p>
        
        <hr>
        <p><em>✅ Ta sestanek je bil sprejet in ustvarjen s strani Meeting Assistant AI.</em></p>
        """
        
        event = self.calendar_ctrl.create_meeting(
            title=pending_meeting.get("title", "Sestanek"),
            start_time=pending_meeting.get("start_time"),
            end_time=pending_meeting.get("end_time"),
            attendees=attendees,
            location=pending_meeting.get("location", "Microsoft Teams"),
            body=body
        )
        
        if event:
            # Označi kot sprejet
            pending_meeting["status"] = "accepted"
            pending_meeting["outlook_event_id"] = event.get("id")
            
            # Označi e-pošto kot prebrano
            if pending_meeting.get("email_id"):
                self.email_ctrl._mark_email_as_read(pending_meeting["email_id"])
            
            return {"success": True, "event": event}
        
        return {"success": False, "error": "Napaka pri ustvarjanju sestanka"}
    
    def reject_meeting(self, meeting_id):
        """Zavrni sestanek - odstrani iz predlogov"""
        
        for i, m in enumerate(st.session_state.pending_meetings):
            if m.get("id") == meeting_id:
                # Označi kot zavrnjen
                m["status"] = "rejected"
                
                # Opcijsko: označi e-pošto kot prebrano
                if m.get("email_id"):
                    self.email_ctrl._mark_email_as_read(m["email_id"])
                
                return {"success": True}
        
        return {"success": False, "error": "Sestanek ni najden"}
    
    def _get_user_email(self):
        """Pridobi email trenutnega uporabnika"""
        from controllers.auth_controller import AuthController
        auth = AuthController()
        user_info = auth.get_user_info()
        return user_info.get('mail', user_info.get('userPrincipalName', '')) if user_info else None
    
    def get_pending_meetings(self):
        """Vrne vse pending sestanke"""
        return [m for m in st.session_state.pending_meetings if m.get("status") == "pending"]
    
    def get_accepted_meetings(self):
        """Vrne vse sprejete sestanke"""
        return [m for m in st.session_state.pending_meetings if m.get("status") == "accepted"]