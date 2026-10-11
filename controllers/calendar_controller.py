# controllers/calendar_controller.py
from datetime import datetime, timedelta
from services.microsoft_graph_service import MicrosoftGraphService
import streamlit as st

class CalendarController:
    def __init__(self, access_token):
        self.graph_service = MicrosoftGraphService(access_token)
    
    def get_meetings(self, limit=50):
        """Pridobi sestanke iz koledarja"""
        return self.graph_service.get_calendar_events(limit)
    
    def get_meeting_details(self, meeting_id):
        """Pridobi podrobnosti sestanka"""
        return self.graph_service.get_event_details(meeting_id)
    
    def create_meeting(self, title, start_time, end_time, attendees, location="", body=""):
        """Ustvari nov sestanek"""
        return self.graph_service.create_event(
            subject=title,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            location=location,
            body=body
        )
    
    def find_free_slots(self, attendees, preferred_date, duration_minutes=60):
        """Najde proste termine za vse udeležence"""
        start_date = preferred_date.replace(hour=0, minute=0, second=0)
        end_date = preferred_date.replace(hour=23, minute=59, second=59)
        
        free_busy = self.graph_service.get_free_busy(attendees, start_date, end_date)
        
        if not free_busy:
            return []
        
        suggestions = []
        work_start = preferred_date.replace(hour=9, minute=0, second=0)
        work_end = preferred_date.replace(hour=17, minute=0, second=0)
        
        current = work_start
        
        while current + timedelta(minutes=duration_minutes) <= work_end:
            slot_end = current + timedelta(minutes=duration_minutes)
            all_free = True
            
            for schedule in free_busy:
                for item in schedule.get("scheduleItems", []):
                    if item.get("status") == "busy":
                        try:
                            avail_start = datetime.fromisoformat(item["start"]["dateTime"].replace('Z', '+00:00'))
                            avail_end = datetime.fromisoformat(item["end"]["dateTime"].replace('Z', '+00:00'))
                            
                            if not (slot_end <= avail_start or current >= avail_end):
                                all_free = False
                                break
                        except:
                            pass
                if not all_free:
                    break
            
            if all_free:
                suggestions.append({
                    "start": current,
                    "end": slot_end,
                    "display": f"{current.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"
                })
            
            current += timedelta(minutes=30)
        
        return suggestions
    
    def suggest_meeting_times(self, attendees, preferred_date, duration_minutes=60):
        """Predlaga termine z alternativami"""
        suggestions = self.find_free_slots(attendees, preferred_date, duration_minutes)
        
        if suggestions:
            return {
                "status": "success",
                "date": preferred_date,
                "suggestions": suggestions
            }
        
        # Poskusi dan prej
        day_before = preferred_date - timedelta(days=1)
        if day_before.weekday() < 5:
            suggestions_before = self.find_free_slots(attendees, day_before, duration_minutes)
            if suggestions_before:
                return {
                    "status": "alternative",
                    "date": day_before,
                    "suggestions": suggestions_before,
                    "message": f"Na {preferred_date.strftime('%d.%m.%Y')} ni prostih terminov. Predlagam {day_before.strftime('%d.%m.%Y')}:"
                }
        
        # Poskusi dan kasneje
        day_after = preferred_date + timedelta(days=1)
        if day_after.weekday() < 5:
            suggestions_after = self.find_free_slots(attendees, day_after, duration_minutes)
            if suggestions_after:
                return {
                    "status": "alternative",
                    "date": day_after,
                    "suggestions": suggestions_after,
                    "message": f"Na {preferred_date.strftime('%d.%m.%Y')} ni prostih terminov. Predlagam {day_after.strftime('%d.%m.%Y')}:"
                }
        
        return {
            "status": "none",
            "message": "Ni prostih terminov. Poskusite z drugim datumom."
        }