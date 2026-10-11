# services/email_analyzer_service.py
import re
from datetime import datetime, timedelta
import streamlit as st

class EmailAnalyzerService:
    """Analizira e-pošto in išče zahteve za sestanke"""
    
    def __init__(self):
        # Ključne besede, ki nakazujejo željo po sestanku
        self.meeting_keywords = [
            r"sestanek", r"meeting", r"call", r"zoom", r"teams",
            r"dobimo se", r"dobesedno", r"pogovorimo",
            r"termin", r"appointment", r"session",
            r"bi se radi dobili", r"bi se radi srečali",
            r"predlagam", r"predlagam termin", r"kdaj bi lahko"
        ]
        
        # Vzorci za datum in uro
        self.date_patterns = [
            r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})",  # 5.6.2026
            r"(\d{4})-(\d{2})-(\d{2})",               # 2026-06-05
            r"(\d{1,2})\.\s*(\d{1,2})\.",             # 5.6.
            r"jutri|tomorrow",
            r"danes|today",
            r"ponedeljek|monday",
            r"torek|tuesday",
            r"sreda|wednesday",
            r"četrtek|thursday",
            r"petek|friday",
        ]
        
        self.time_patterns = [
            r"(\d{1,2})[:.](\d{2})",      # 14:30 ali 14.30
            r"(\d{1,2})\s*uri",            # 14 uri
            r"(\d{1,2})\s*:\s*(\d{2})",
        ]
    
    def analyze_email(self, subject, body, sender):
        """Analizira e-pošto in vrne informacije o morebitnem sestanku"""
        
        full_text = f"{subject} {body}".lower()
        
        # Preveri, ali e-pošta vsebuje zahtevo za sestanek
        is_meeting_request = False
        matched_keyword = None
        
        for keyword in self.meeting_keywords:
            if re.search(keyword, full_text, re.IGNORECASE):
                is_meeting_request = True
                matched_keyword = keyword
                break
        
        if not is_meeting_request:
            return None
        
        # Poskusi izluščiti datum
        meeting_date = self._extract_date(full_text)
        
        # Poskusi izluščiti uro
        meeting_time = self._extract_time(full_text)
        
        # Poskusi izluščiti trajanje
        duration = self._extract_duration(full_text)
        
        # Poskusi izluščiti lokacijo
        location = self._extract_location(full_text, body)
        
        # Poskusi izluščiti naslov sestanka
        meeting_title = self._extract_title(subject, full_text)
        
        # Poskusi izluščiti dodatne udeležence
        additional_attendees = self._extract_attendees(full_text, sender)
        
        return {
            "is_meeting_request": True,
            "matched_keyword": matched_keyword,
            "sender": sender,
            "subject": subject,
            "meeting_title": meeting_title,
            "suggested_date": meeting_date,
            "suggested_time": meeting_time,
            "suggested_duration": duration,
            "suggested_location": location,
            "additional_attendees": additional_attendees,
            "original_body": body[:500]  # Shrani del originalnega sporočila
        }
    
    def _extract_date(self, text):
        """Izlušči datum iz besedila"""
        today = datetime.now()
        
        # Poskusi najti ekspliciten datum
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if pattern == r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})":
                    day, month, year = match.groups()
                    try:
                        return datetime(int(year), int(month), int(day))
                    except:
                        pass
                
                elif pattern == r"(\d{4})-(\d{2})-(\d{2})":
                    year, month, day = match.groups()
                    try:
                        return datetime(int(year), int(month), int(day))
                    except:
                        pass
                
                elif pattern == r"(\d{1,2})\.\s*(\d{1,2})\.":
                    day, month = match.groups()
                    try:
                        year = today.year
                        if int(month) < today.month:
                            year += 1
                        return datetime(year, int(month), int(day))
                    except:
                        pass
                
                elif pattern == r"jutri|tomorrow":
                    return today + timedelta(days=1)
                
                elif pattern == r"danes|today":
                    return today
                
                elif pattern == r"ponedeljek|monday":
                    days_ahead = 0 - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    return today + timedelta(days=days_ahead)
                
                elif pattern == r"torek|tuesday":
                    days_ahead = 1 - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    return today + timedelta(days=days_ahead)
                
                elif pattern == r"sreda|wednesday":
                    days_ahead = 2 - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    return today + timedelta(days=days_ahead)
                
                elif pattern == r"četrtek|thursday":
                    days_ahead = 3 - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    return today + timedelta(days=days_ahead)
                
                elif pattern == r"petek|friday":
                    days_ahead = 4 - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    return today + timedelta(days=days_ahead)
        
        return None
    
    def _extract_time(self, text):
        """Izlušči uro iz besedila"""
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if pattern == r"(\d{1,2})[:.](\d{2})":
                    hour, minute = match.groups()
                    return (int(hour), int(minute))
                elif pattern == r"(\d{1,2})\s*uri":
                    hour = match.group(1)
                    return (int(hour), 0)
        return None
    
    def _extract_duration(self, text):
        """Izlušči trajanje sestanka"""
        patterns = [
            (r"(\d+)\s*ur", 60),      # X ur
            (r"(\d+)\s*minut", 1),     # X minut
            (r"(\d+)\s*min", 1),
            (r"pol ure", 30),
            (r"half hour", 30),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if multiplier == 60:
                    return int(match.group(1)) * 60
                elif multiplier == 1:
                    return int(match.group(1))
                else:
                    return multiplier
        
        # Default trajanje
        return 60
    
    def _extract_location(self, text, body):
        """Izlušči lokacijo sestanka"""
        if "teams" in text or "zoom" in text:
            return "Microsoft Teams (online)"
        
        location_patterns = [
            r"v (?:prostoru|sobi|sali)\s+([^,.]+)",
            r"location:\s*([^,\n]+)",
            r"kraj:\s*([^,\n]+)",
            r"at\s+([^,\n]+)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Sejna soba"
    
    def _extract_title(self, subject, body):
        """Izlušči naslov sestanka"""
        # Najprej poskusi s subjectom
        if subject and not re.match(r'(re:|fwd:|odg:)', subject, re.IGNORECASE):
            # Odstrani ključne besede iz naslova
            title = re.sub(r'(sestanek|meeting|predlog|proposal)', '', subject, flags=re.IGNORECASE)
            title = title.strip()
            if title and len(title) > 5:
                return title
        
        # Poskusi najti v telesu
        patterns = [
            r"naslov sestanka:\s*([^\n]+)",
            r"title:\s*([^\n]+)",
            r"o\s+temi:\s*([^\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Sestanek"
    
    def _extract_attendees(self, text, sender):
        """Izlušči dodatne udeležence"""
        attendees = [sender] if sender else []
        
        # Poišči email naslove
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text)
        
        for email in emails:
            if email not in attendees:
                attendees.append(email)
        
        return attendees