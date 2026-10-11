# views/pages/tasks_page.py
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.todo_controller import TodoController
from utils.helpers import format_date


def show_tasks_page():
    auth = AuthController()

    if not auth.is_authenticated():
        st.warning("Za ogled nalog se morate prijaviti")
        return

    head, btn = st.columns([5, 1])
    with head:
        st.title("Moje naloge")
        st.caption("Naloge iz Microsoft To-Do")
    with btn:
        st.write("")
        if st.button("Osveži", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    todo_ctrl = TodoController(auth.get_access_token())

    with st.spinner("Nalaganje nalog iz Microsoft To-Do..."):
        tasks = todo_ctrl.get_all_tasks()

    # Hitro dodajanje
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            quick_task = st.text_input(
                "Nova naloga", placeholder="Vpiši nalogo...", key="quick_task_input",
                label_visibility="collapsed",
            )
        with col2:
            if st.button("Dodaj", use_container_width=True, type="primary", key="quick_add_btn"):
                if quick_task:
                    if todo_ctrl.add_task_from_meeting(quick_task, "Hitro dodana naloga"):
                        st.rerun()
                    else:
                        st.error("Napaka pri dodajanju")

    if not tasks:
        st.write("")
        st.markdown(
            '<div class="empty-state">Ni nalog v Microsoft To-Do. Dodajte jih iz sestankov ali ročno zgoraj.</div>',
            unsafe_allow_html=True,
        )
        return

    filter_option = st.radio(
        "Prikaži",
        ["Vse naloge", "Aktivne naloge", "Dokončane naloge"],
        horizontal=True,
        label_visibility="collapsed",
    )

    tasks_by_list = {}
    for task in tasks:
        status = task.get("status", "notStarted")
        if filter_option == "Aktivne naloge" and status == "completed":
            continue
        if filter_option == "Dokončane naloge" and status != "completed":
            continue
        tasks_by_list.setdefault(task.get("list_name", "Ostalo"), []).append(task)

    if not tasks_by_list:
        st.markdown('<div class="empty-state">Ni nalog za izbrani filter.</div>', unsafe_allow_html=True)
        return

    for list_name, list_tasks in tasks_by_list.items():
        st.markdown(f'<div class="section-title">{list_name}</div>', unsafe_allow_html=True)

        for task in list_tasks:
            title = task.get("title", "Brez naslova")
            status = task.get("status", "notStarted")
            task_id = task.get("id")
            list_id = task.get("list_id")
            due_date = task.get("dueDateTime", {}).get("dateTime", "") if task.get("dueDateTime") else ""
            body = task.get("body", {}).get("content", "")
            done = status == "completed"

            with st.container(border=True):
                col_info, col_btn = st.columns([5, 1])

                with col_info:
                    title_html = f'<span class="task-done">{title}</span>' if done else title
                    badge = '<span class="badge badge--ok">Dokončano</span>' if done else ""
                    meta = f'<div class="row-meta">Rok: {format_date(due_date)}</div>' if due_date else ""
                    st.markdown(f'<div class="row-title">{title_html}{badge}</div>{meta}', unsafe_allow_html=True)

                with col_btn:
                    if not done:
                        if st.button("Dokončaj", key=f"complete_{list_id}_{task_id}", use_container_width=True):
                            if todo_ctrl.complete_task(list_id, task_id):
                                st.rerun()

                if body:
                    with st.expander("Podrobnosti"):
                        st.write(body)