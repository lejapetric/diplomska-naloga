# views/pages/tasks_page.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.todo_controller import TodoController
from utils.helpers import format_date

def show_tasks_page():
    st.title("✅ Moje naloge")
    
    auth = AuthController()
    
    if not auth.is_authenticated():
        st.warning("Za ogled nalog se morate prijaviti")
        return
    
    # Refresh gumb
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Osveži", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    todo_ctrl = TodoController(auth.get_access_token())
    
    with st.spinner("Nalaganje nalog iz Microsoft To-Do..."):
        tasks = todo_ctrl.get_all_tasks()
    
    # Hitro dodajanje naloge
    st.markdown("### ➕ Hitro dodaj nalogo")
    col1, col2 = st.columns([3, 1])
    with col1:
        quick_task = st.text_input("Nova naloga", placeholder="Vpiši nalogo...", key="quick_task_input")
    with col2:
        if st.button("Dodaj", use_container_width=True, key="quick_add_btn"):
            if quick_task:
                result = todo_ctrl.add_task_from_meeting(quick_task, "Hitro dodana naloga")
                if result:
                    st.success("Naloga dodana!")
                    st.rerun()
                else:
                    st.error("Napaka pri dodajanju")
    
    st.markdown("---")
    
    if tasks:
        # Filter
        filter_option = st.selectbox(
            "Prikaži",
            ["Vse naloge", "Aktivne naloge", "Dokončane naloge"]
        )
        
        # Razvrsti po listah
        tasks_by_list = {}
        for task in tasks:
            list_name = task.get("list_name", "Ostalo")
            status = task.get("status", "notStarted")
            
            if filter_option == "Aktivne naloge" and status == "completed":
                continue
            if filter_option == "Dokončane naloge" and status != "completed":
                continue
            
            if list_name not in tasks_by_list:
                tasks_by_list[list_name] = []
            tasks_by_list[list_name].append(task)
        
        for list_name, list_tasks in tasks_by_list.items():
            st.markdown(f"### 📁 {list_name}")
            
            for task in list_tasks:
                task_title = task.get("title", "Brez naslova")
                task_status = task.get("status", "notStarted")
                task_id = task.get("id")
                list_id = task.get("list_id")
                due_date = task.get("dueDateTime", {}).get("dateTime", "") if task.get("dueDateTime") else ""
                body = task.get("body", {}).get("content", "")
                
                with st.container():
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        if task_status == "completed":
                            st.markdown(f"~~{task_title}~~ ✅")
                        else:
                            st.write(task_title)
                        
                        if due_date:
                            st.caption(f"📅 Rok: {format_date(due_date)}")
                    
                    with col2:
                        if task_status != "completed":
                            if st.button(f"✅ Dokončaj", key=f"complete_{list_id}_{task_id}"):
                                if todo_ctrl.complete_task(list_id, task_id):
                                    st.success("Naloga dokončana!")
                                    st.rerun()
                    
                    with col3:
                        if st.button(f"📄", key=f"detail_{list_id}_{task_id}"):
                            if body:
                                st.info(body)
                            else:
                                st.info("Ni podrobnosti")
                    
                    st.divider()
    
    else:
        st.info("📭 Ni nalog v Microsoft To-Do. Dodajte jih iz sestankov ali ročno zgoraj!")