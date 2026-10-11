# services/openai_service.py
import json
from openai import OpenAI
from config.settings import OPENAI_API_KEY
import streamlit as st

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    def is_available(self):
        return self.client is not None and OPENAI_API_KEY is not None
    
    def generate_summary(self, meeting_title, content, language="slovenian"):
        """Generira povzetek sestanka"""
        if not self.is_available():
            return "⚠️ OpenAI API ključ ni nastavljen. Dodajte ga v .env datoteko."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a professional meeting assistant. Create a concise summary (max 200 words) in {language} language. Focus on key decisions, main discussion points, and action items."},
                    {"role": "user", "content": f"Meeting title: {meeting_title}\n\nMeeting content:\n{content[:4000]}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Napaka pri generiranju povzetka: {str(e)}"
    
    def extract_action_items(self, content):
        """Izlušči naloge iz vsebine"""
        if not self.is_available():
            return [{"task": "Dodaj OpenAI API ključ v .env", "assignee": "Admin", "due_date": "TBD"}]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """Iz spodnje vsebine sestanka izlušči vse naloge.
                    
Pravila:
1. Vrni SAMO JSON array, brez drugega besedila
2. Vsaka naloga naj ima: task (opis naloge), assignee (odgovorna oseba - če ni omenjena daj "TBD"), due_date (rok v formatu YYYY-MM-DD - če ni daj "TBD")
3. Če ni nobene naloge, vrni prazen array []

Primer odgovora:
[
    {"task": "Pripraviti poročilo", "assignee": "Ana Novak", "due_date": "2026-06-20"},
    {"task": "Posodobiti spletno stran", "assignee": "TBD", "due_date": "TBD"}
]"""},
                    {"role": "user", "content": content[:4000]}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            result = response.choices[0].message.content.strip()
            
            # Očisti odgovor
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            # Poskusi parsati JSON
            parsed = json.loads(result)
            
            # Če ni array, naredi array
            if not isinstance(parsed, list):
                if isinstance(parsed, dict):
                    parsed = [parsed]
                else:
                    parsed = []
            
            return parsed
            
        except json.JSONDecodeError:
            return [{"task": "Napaka pri parsanju JSON", "assignee": "TBD", "due_date": "TBD"}]
        except Exception as e:
            return [{"task": f"Napaka pri ekstrakciji: {str(e)}", "assignee": "TBD", "due_date": "TBD"}]
    
    def suggest_meeting_topics(self, context=""):
        """Predlaga teme za dnevni red sestanka"""
        if not self.is_available():
            return [
                "📊 Pregled stanja projektov",
                "✅ Naloge iz prejšnjega sestanka",
                "🎯 Ključni cilji za tekoči teden",
                "⚠️ Težave in izzivi",
                "📅 Načrt za prihodnji teden"
            ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Predlagaj 5-7 točk za dnevni red sestanka. Vsako točko napiši v novo vrstico, začni z emojijem. Naj bodo točke konkretne in uporabne."},
                    {"role": "user", "content": f"Kontekst sestanka: {context if context else 'Splošni delovni sestanek'}"}
                ],
                max_tokens=300,
                temperature=0.8
            )
            topics = response.choices[0].message.content.split('\n')
            return [t.strip() for t in topics if t.strip()]
        except:
            return ["Pregled stanja", "Naloge iz prejšnjega sestanka", "Načrt za naprej"]