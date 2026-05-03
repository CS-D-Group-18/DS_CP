import customtkinter as ctk

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        # Configure layout
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Welcome Section
        self.welcome_label = ctk.CTkLabel(
            self, text="Dashboard Overview", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#1e2022"
        )
        self.welcome_label.grid(row=0, column=0, columnspan=4, pady=(25, 5), sticky="w", padx=30)
        
        self.subtitle_label = ctk.CTkLabel(
            self, text="Real-time simulation metrics and scheduling analytics", 
            text_color="#6c757d", font=ctk.CTkFont(family="Inter", size=13)
        )
        self.subtitle_label.grid(row=1, column=0, columnspan=4, pady=(0, 20), sticky="w", padx=30)

        # Statistics Cards Area
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, columnspan=4, sticky="new", padx=20)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Cards (SaaS style: rounded corners, icons, large numbers)
        self.total_card = self.create_stat_card(self.stats_frame, "📋 Total Tasks", "0", 0, "#3b82f6") # Blue
        self.pending_card = self.create_stat_card(self.stats_frame, "⏳ Pending", "0", 1, "#f59e0b") # Amber
        self.completed_card = self.create_stat_card(self.stats_frame, "✅ Completed", "0", 2, "#10b981") # Emerald
        self.cpu_card = self.create_stat_card(self.stats_frame, "⏱️ Total Time", "0", 3, "#8b5cf6") # Violet

        # Quick Actions
        self.actions_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#e5e7eb")
        self.actions_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=(30, 10), pady=20)
        
        actions_label = ctk.CTkLabel(self.actions_frame, text="Quick Actions", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#111827")
        actions_label.pack(pady=(20, 15), padx=25, anchor="w")
        
        ctk.CTkButton(self.actions_frame, text="➕ Add New Task", height=42, corner_radius=8, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), fg_color="#f3f4f6", text_color="#374151", hover_color="#e5e7eb", command=lambda: self.nav_callback("tasks")).pack(pady=8, padx=25, fill="x")
        ctk.CTkButton(self.actions_frame, text="🔗 Add Dependency", height=42, corner_radius=8, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), fg_color="#f3f4f6", text_color="#374151", hover_color="#e5e7eb", command=lambda: self.nav_callback("dependencies")).pack(pady=8, padx=25, fill="x")
        ctk.CTkButton(self.actions_frame, text="▶ Run Scheduler", height=46, corner_radius=8, font=ctk.CTkFont(family="Inter", size=15, weight="bold"), fg_color="#4f46e5", text_color="white", hover_color="#4338ca", command=lambda: self.nav_callback("scheduler")).pack(pady=(15, 8), padx=25, fill="x")
        ctk.CTkButton(self.actions_frame, text="🚀 Load Demo Data", height=42, corner_radius=8, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), fg_color="#10b981", text_color="white", hover_color="#059669", command=self.load_demo_data).pack(pady=8, padx=25, fill="x")

        # Recent Logs (Preview)
        self.logs_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color="#e5e7eb")
        self.logs_frame.grid(row=3, column=2, columnspan=2, sticky="nsew", padx=(10, 30), pady=20)
        
        logs_label = ctk.CTkLabel(self.logs_frame, text="Execution Logs", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#111827")
        logs_label.pack(pady=(20, 15), padx=25, anchor="w")
        
        self.log_textbox = ctk.CTkTextbox(self.logs_frame, wrap="word", state="disabled", font=ctk.CTkFont(family="Consolas", size=13), fg_color="#111827", text_color="#e5e7eb", corner_radius=8)
        self.log_textbox.pack(expand=True, fill="both", padx=25, pady=(0, 25))
        
        self.log_textbox.tag_config("running", foreground="#60a5fa") # Blue
        self.log_textbox.tag_config("completed", foreground="#34d399") # Green
        self.log_textbox.tag_config("waiting", foreground="#fbbf24") # Yellow

    def create_stat_card(self, parent, title, value, col, highlight_color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=1, border_color="#e5e7eb")
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        
        # Add a subtle top border indicator for highlight color
        indicator = ctk.CTkFrame(card, fg_color=highlight_color, height=4, corner_radius=0)
        indicator.pack(fill="x", side="top", pady=0)
        
        title_lbl = ctk.CTkLabel(card, text=title, text_color="#6b7280", font=ctk.CTkFont(family="Inter", size=14, weight="bold"))
        title_lbl.pack(pady=(15, 0), padx=20, anchor="w")
        
        value_lbl = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family="Inter", size=38, weight="bold"), text_color="#111827")
        value_lbl.pack(pady=(5, 20), padx=20, anchor="w")
        return value_lbl

    def update_data(self):
        """Called whenever the dashboard is shown to refresh stats."""
        total = len(self.engine.tasks)
        completed = len(self.engine.completed_tasks)
        pending = total - completed
        
        self.total_card.configure(text=str(total))
        self.completed_card.configure(text=str(completed))
        self.pending_card.configure(text=str(pending))
        
        # Total simulation time (from engine.current_time)
        self.cpu_card.configure(text=str(self.engine.current_time))
        
        # Update logs preview
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        
        if not self.engine.execution_log:
            self.log_textbox.insert("end", "No logs available. Run the scheduler first.")
        else:
            # Show last 5 log entries
            recent_logs = self.engine.execution_log[-5:]
            for log in recent_logs:
                tag = None
                if "Running" in log:
                    tag = "running"
                elif "COMPLETED" in log:
                    tag = "completed"
                elif "arrived" in log or "waiting" in log:
                    tag = "waiting"
                    
                if tag:
                    self.log_textbox.insert("end", log + "\n", tag)
                else:
                    self.log_textbox.insert("end", log + "\n")
        self.log_textbox.configure(state="disabled")

    def load_demo_data(self):
        """Loads a proper example to generate reports immediately."""
        from task import Task
        # Clear existing
        self.engine.tasks.clear()
        self.engine.dag_manager.adj_list.clear()
        self.engine.dag_manager.in_degree.clear()
        
        # Add tasks
        self.engine.add_task(Task("T1", "Database Backup", 1, 4, 15, 0))
        self.engine.add_task(Task("T2", "API Request", 2, 2, 5, 1))
        self.engine.add_task(Task("T3", "Process Images", 3, 5, 20, 2))
        self.engine.add_task(Task("T4", "Send Emails", 2, 3, 0, 3))
        self.engine.add_task(Task("T5", "Generate Report", 1, 6, 25, 4))
        
        # Add dependencies
        self.engine.dag_manager.add_dependency("T1", "T5")
        self.engine.dag_manager.add_dependency("T2", "T3")
        self.engine.dag_manager.add_dependency("T3", "T5")
        
        # Run simulation
        self.engine.run("Priority")
        self.update_data()
        self.nav_callback("reports")
