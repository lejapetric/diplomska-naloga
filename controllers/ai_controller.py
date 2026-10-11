# controllers/ai_controller.py
from services.openai_service import OpenAIService
from controllers.onenote_controller import OneNoteController
import streamlit as st

class AIController:
    def __init__(self, access_token=None):
        self.ai_service = OpenAIService()
        self.onenote_controller = OneNoteController(access_token) if access_token else None
        self.access_token = access_token
    
    def is_ai_available(self):
        return self.ai_service.is_available()
    
    def process_meeting_content(self, title, content):
        """Obdela vsebino sestanka - generira povzetek in naloge"""
        if not self.ai_service.is_available():
            return {
                "success": False,
                "error": "OpenAI API ključ ni nastavljen. Dodajte ga v .env datoteko.",
                "summary": None,
                "action_items": None
            }
        
        with st.spinner("🤖 AI generira povzetek..."):
            summary = self.ai_service.generate_summary(title, content)
        
        with st.spinner("🤖 AI izlušča naloge..."):
            action_items = self.ai_service.extract_action_items(content)
        
        return {
            "success": True,
            "summary": summary,
            "action_items": action_items
        }
    
    def generate_summary_only(self, title, content):
        """Generira samo povzetek"""
        return self.ai_service.generate_summary(title, content)
    
    def extract_tasks_only(self, content):
        """Izlušči samo naloge"""
        return self.ai_service.extract_action_items(content)
    
    def process_and_save_to_onenote(self, title, content, meeting_date, attendees, file_name=None):
        """Obdela sestanek in shrani v OneNote"""
        # Procesiraj z AI
        result = self.process_meeting_content(title, content)
        
        if not result["success"]:
            return result
        
        # Shrani v OneNote
        if self.onenote_controller and self.access_token:
            onenote_result = self.onenote_controller.save_meeting_summary(
                meeting_title=title,
                summary=result["summary"],
                action_items=result["action_items"],
                meeting_date=meeting_date,
                attendees=attendees or []
            )
            
            return {
                "success": True,
                "summary": result["summary"],
                "action_items": result["action_items"],
                "onenote_page": onenote_result
            }
        
        return {
            "success": True,
            "summary": result["summary"],
            "action_items": result["action_items"],
            "onenote_page": None
        }
    
    def suggest_meeting_agenda(self, context=""):
        """Predlaga dnevni red za sestanek"""
        if not self.ai_service.is_available():
            return [
                "Pregled preteklih nalog",
                "Diskusija o napredku",
                "Nove naloge in odgovornosti",
                "Načrtovanje prihodnjih korakov",
                "Razno"
            ]
        
        return self.ai_service.suggest_meeting_topics(context)