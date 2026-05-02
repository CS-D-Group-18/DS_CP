import customtkinter as ctk

class LogsPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(self, text="📜 Execution Logs", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"))
        title_label.grid(row=0, column=0, pady=(30, 10), padx=30, sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(self, wrap="word", state="disabled", font=ctk.CTkFont(family="Consolas", size=14), fg_color="#1e1e1e", text_color="#d4d4d4", corner_radius=10)
        self.log_textbox.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew")
        
        self.log_textbox.tag_config("running", foreground="#569cd6") # VSCode Blue
        self.log_textbox.tag_config("completed", foreground="#4ec9b0") # VSCode Green
        self.log_textbox.tag_config("waiting", foreground="#ce9178") # VSCode Orange/Red

    def update_data(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        
        if not self.engine.execution_log:
            self.log_textbox.insert("end", "No logs available. Run the scheduler first.")
        else:
            for log in self.engine.execution_log:
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
