# utils/helpers.py
from datetime import datetime
import re

def format_datetime(dt_string):
    """Formatira datetime za lepši prikaz"""
    if not dt_string:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y ob %H:%M")
    except:
        return dt_string[:16] if len(dt_string) > 16 else dt_string

def format_date(date_string):
    """Formatira samo datum"""
    if not date_string:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y")
    except:
        return date_string[:10] if len(date_string) > 10 else date_string

def parse_attendees(attendees_input):
    """Parsira seznam udeležencev iz text area"""
    if not attendees_input:
        return []
    
    emails = []
    for line in attendees_input.split('\n'):
        email = line.strip()
        if email and validate_email(email):
            emails.append(email)
    
    return emails

def validate_email(email):
    """Preveri ali je email veljaven"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text, max_length=200):
    """Skrajša besedilo"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def get_file_icon(filename):
    """Vrne ikono glede na tip datoteke"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    icons = {
        'txt': '📄',
        'vtt': '📝',
        'mp3': '🎙️',
        'mp4': '🎥',
        'pdf': '📑',
        'doc': '📘',
        'docx': '📘',
        'xls': '📊',
        'xlsx': '📊'
    }
    
    return icons.get(ext, '📁')

def get_status_badge(status):
    """Vrne HTML značko za status"""
    badges = {
        'pending': ('🟡', 'Čaka'),
        'completed': ('✅', 'Dokončano'),
        'in_progress': ('🔵', 'V teku'),
        'cancelled': ('❌', 'Preklicano')
    }
    
    color, text = badges.get(status, ('⚪', status))
    return f'<span style="background: #f0f0f0; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">{color} {text}</span>'