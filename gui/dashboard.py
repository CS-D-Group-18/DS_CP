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
        """Loads a comprehensive Enterprise Cloud Deployment example."""
        from task import Task
        # Properly reset the engine and DAG state
        self.engine.reset()
        
        # 1. Infrastructure Tasks
        self.engine.add_task(Task("INF-101", "Provision Cloud VPC", 1, 5, 20, 0))
        self.engine.add_task(Task("INF-102", "Configure Firewall", 2, 3, 25, 0))
        
        # 2. Database & Storage (Depends on Infra)
        self.engine.add_task(Task("DB-201", "Setup PostgreSQL Cluster", 2, 6, 30, 2))
        self.engine.add_task(Task("STR-202", "S3 Bucket Provisioning", 3, 2, 35, 2))
        
        # 3. Application Builds (Can start early but needs infra)
        self.engine.add_task(Task("APP-301", "Build Backend Image", 3, 8, 40, 0))
        self.engine.add_task(Task("APP-302", "Compile Frontend Assets", 4, 4, 40, 0))
        
        # 4. Deployment & Testing
        self.engine.add_task(Task("DEP-401", "Stage Deploy", 2, 4, 50, 5))
        self.engine.add_task(Task("TST-402", "Run Integration Tests", 1, 10, 70, 5))
        self.engine.add_task(Task("PRD-501", "Production Rollout", 1, 5, 100, 10))
        
        # Define Dependencies
        # Infrastructure must be ready for DB and Firewall
        self.engine.dag_manager.add_dependency("INF-101", "DB-201")
        self.engine.dag_manager.add_dependency("INF-101", "INF-102")
        
        # Deploy depends on DB, Firewall, and Builds
        self.engine.dag_manager.add_dependency("DB-201", "DEP-401")
        self.engine.dag_manager.add_dependency("INF-102", "DEP-401")
        self.engine.dag_manager.add_dependency("APP-301", "DEP-401")
        self.engine.dag_manager.add_dependency("APP-302", "DEP-401")
        
        # Testing depends on Staging
        self.engine.dag_manager.add_dependency("DEP-401", "TST-402")
        
        # Production depends on Testing and S3 Storage
        self.engine.dag_manager.add_dependency("TST-402", "PRD-501")
        self.engine.dag_manager.add_dependency("STR-202", "PRD-501")
        
        # Run simulation with default Priority algorithm
        self.engine.run("Priority")
        self.update_data()
        self.nav_callback("reports")
