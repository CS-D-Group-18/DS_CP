import customtkinter as ctk
from tkinter import messagebox
from task import Task, TaskStatus

class TaskPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        # Title
        title_label = ctk.CTkLabel(self, text="Task Management", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Tabs for Add and Manage
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=(0, 20))
        
        self.tab_add = self.tabview.add("Add Task")
        self.tab_manage = self.tabview.add("Manage Tasks")
        
        self.setup_add_tab()
        self.setup_manage_tab()

    def setup_add_tab(self):
        # Configure grid layout for the form
        self.tab_add.grid_columnconfigure((0, 1), weight=1)
        
        form_frame = ctk.CTkFrame(self.tab_add)
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form Fields
        self.entries = {}
        fields = [
            ("Task ID (e.g., T1):", "task_id", ""),
            ("Task Name:", "name", ""),
            ("Priority (lower = higher priority):", "priority", "0"),
            ("Execution Time:", "exec_time", "5"),
            ("Deadline (0 if none):", "deadline", "0"),
            ("Arrival Time:", "arrival_time", "0")
        ]
        
        for i, (label_text, key, default) in enumerate(fields):
            lbl = ctk.CTkLabel(form_frame, text=label_text)
            lbl.grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            entry = ctk.CTkEntry(form_frame, placeholder_text=f"Enter {key}")
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
            self.entries[key] = entry
            
        # Add Button
        add_btn = ctk.CTkButton(form_frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=len(fields), column=0, columnspan=2, pady=30)

    def add_task(self):
        try:
            task_id = self.entries["task_id"].get().strip()
            name = self.entries["name"].get().strip()
            
            if not task_id or not name:
                messagebox.showerror("Error", "Task ID and Name are required.")
                return
                
            if task_id in self.engine.tasks:
                messagebox.showerror("Error", f"Task ID '{task_id}' already exists.")
                return

            priority = int(self.entries["priority"].get())
            exec_time = int(self.entries["exec_time"].get())
            deadline = int(self.entries["deadline"].get())
            arrival_time = int(self.entries["arrival_time"].get())
            
            if exec_time < 0 or arrival_time < 0:
                messagebox.showerror("Error", "Execution time and Arrival time cannot be negative.")
                return

            new_task = Task(task_id, name, priority, exec_time, deadline, arrival_time)
            self.engine.add_task(new_task)
            
            messagebox.showinfo("Success", f"Task '{name}' added successfully.")
            self.clear_form()
            self.refresh_table()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers for numerical fields.")
            
    def clear_form(self):
        self.entries["task_id"].delete(0, "end")
        self.entries["name"].delete(0, "end")
        # Keep defaults for numbers mostly intact, or reset them
        for key in ["priority", "exec_time", "deadline", "arrival_time"]:
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, "0")

    def setup_manage_tab(self):
        self.tab_manage.grid_columnconfigure(0, weight=1)
        self.tab_manage.grid_rowconfigure(1, weight=1)
        
        # Top Bar (Search & Sort)
        top_bar = ctk.CTkFrame(self.tab_manage, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_table())
        search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search tasks...", textvariable=self.search_var, width=200)
        search_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(top_bar, text="Sort by:").pack(side="left", padx=(10, 5))
        self.sort_var = ctk.StringVar(value="Arrival Time")
        sort_dropdown = ctk.CTkOptionMenu(top_bar, values=["Arrival Time", "Priority", "Deadline"], variable=self.sort_var, command=lambda _: self.refresh_table())
        sort_dropdown.pack(side="left")

        # Scrollable Frame for Table
        self.table_frame = ctk.CTkScrollableFrame(self.tab_manage)
        self.table_frame.grid(row=1, column=0, sticky="nsew")
        
        self.refresh_table()

    def get_status_color(self, status):
        colors = {
            TaskStatus.PENDING: "orange",
            TaskStatus.RUNNING: "blue",
            TaskStatus.COMPLETED: "green",
            TaskStatus.MISSED: "red",
            TaskStatus.DELETED: "gray"
        }
        return colors.get(status, "white")

    def refresh_table(self):
        # Clear existing rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        # Headers
        headers = ["ID", "Name", "Pri", "Exec", "Dead", "Arr", "Status", "Actions"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=10, pady=5, sticky="w")
            
        tasks = list(self.engine.tasks.values())
        
        # Filter
        search_term = self.search_var.get().lower()
        if search_term:
            tasks = [t for t in tasks if search_term in t.task_id.lower() or search_term in t.name.lower()]
            
        # Sort
        sort_by = self.sort_var.get()
        if sort_by == "Priority":
            tasks.sort(key=lambda x: x.priority)
        elif sort_by == "Deadline":
            # Treat 0 deadline as max to push to end
            tasks.sort(key=lambda x: x.deadline if x.deadline > 0 else float('inf'))
        else: # Arrival Time
            tasks.sort(key=lambda x: x.arrival_time)
            
        # Rows
        for row, task in enumerate(tasks, start=1):
            ctk.CTkLabel(self.table_frame, text=task.task_id).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=task.name).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(task.priority)).grid(row=row, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(task.exec_time)).grid(row=row, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(task.deadline) if task.deadline else "-").grid(row=row, column=4, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(task.arrival_time)).grid(row=row, column=5, padx=10, pady=5, sticky="w")
            
            # Status badge
            status_lbl = ctk.CTkLabel(self.table_frame, text=task.status.name, text_color=self.get_status_color(task.status))
            status_lbl.grid(row=row, column=6, padx=10, pady=5, sticky="w")
            
            # Action buttons
            btn_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=7, padx=10, pady=5, sticky="w")
            
            del_btn = ctk.CTkButton(btn_frame, text="Del", width=40, fg_color="#D32F2F", hover_color="#B71C1C", 
                                    command=lambda t_id=task.task_id: self.delete_task(t_id))
            del_btn.pack(side="left")

    def delete_task(self, task_id):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Task {task_id}?"):
            # Mark as deleted (lazy deletion for simulation)
            self.engine.tasks[task_id].status = TaskStatus.DELETED
            self.refresh_table()

    def update_data(self):
        """Refresh when page is visited."""
        self.refresh_table()
