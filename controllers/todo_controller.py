# controllers/todo_controller.py
import requests
from services.microsoft_graph_service import MicrosoftGraphService
import streamlit as st

class TodoController:
    def __init__(self, access_token):
        self.graph_service = MicrosoftGraphService(access_token)
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def get_or_create_meeting_list(self):
        """Poišče ali ustvari 'Meeting Tasks' listo"""
        lists = self.graph_service.get_todo_lists()
        
        for task_list in lists:
            if task_list.get("displayName") == "Meeting Tasks":
                return task_list
        
        # Ustvari novo listo
        url = "https://graph.microsoft.com/v1.0/me/todo/lists"
        data = {"displayName": "Meeting Tasks"}
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                return response.json()
        except Exception as e:
            st.error(f"Napaka pri ustvarjanju liste: {str(e)}")
        
        return None
    
    def add_task_from_meeting(self, task_title, meeting_title, due_date=None, assignee=None):
        """Doda nalogo iz sestanka v To-Do"""
        task_list = self.get_or_create_meeting_list()
        
        if not task_list:
            return None
        
        list_id = task_list.get("id")
        
        # Pripravi podrobnosti naloge
        details = f"Iz sestanka: {meeting_title}"
        if assignee:
            details += f"\nOdgovoren: {assignee}"
        
        return self.graph_service.create_todo_task(list_id, task_title, details, due_date)
    
    def add_multiple_tasks(self, tasks, meeting_title):
        """Doda več nalog naenkrat"""
        added_tasks = []
        
        for task in tasks:
            if isinstance(task, dict):
                task_title = task.get("task", "")
                assignee = task.get("assignee", None)
                due_date = task.get("due_date", None)
            else:
                task_title = str(task)
                assignee = None
                due_date = None
            
            if task_title:
                result = self.add_task_from_meeting(task_title, meeting_title, due_date, assignee)
                if result:
                    added_tasks.append(task_title)
        
        return added_tasks
    
    def get_all_tasks(self):
        """Pridobi vse naloge iz vseh list"""
        lists = self.graph_service.get_todo_lists()
        all_tasks = []
        
        for task_list in lists:
            list_id = task_list.get("id")
            list_name = task_list.get("displayName")
            
            url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks"
            
            try:
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    tasks = response.json().get("value", [])
                    for task in tasks:
                        task["list_name"] = list_name
                        task["list_id"] = list_id
                        all_tasks.append(task)
            except Exception as e:
                st.error(f"Napaka pri nalaganju nalog: {str(e)}")
        
        return all_tasks
    
    def complete_task(self, list_id, task_id):
        """Označi nalogo kot dokončano"""
        url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks/{task_id}"
        data = {"status": "completed"}
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            return response.status_code == 200
        except Exception as e:
            st.error(f"Napaka pri zaključevanju naloge: {str(e)}")
            return False
    
    def delete_task(self, list_id, task_id):
        """Izbriše nalogo"""
        url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks/{task_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            return response.status_code == 204
        except Exception as e:
            st.error(f"Napaka pri brisanju naloge: {str(e)}")
            return False