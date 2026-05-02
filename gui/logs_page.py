import customtkinter as ctk

class LogsPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(self, text="Execution Logs", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(self, wrap="word", state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def update_data(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        
        if not self.engine.execution_log:
            self.log_textbox.insert("end", "No logs available. Run the scheduler first.")
        else:
            for log in self.engine.execution_log:
                self.log_textbox.insert("end", log + "\n")
                
        self.log_textbox.configure(state="disabled")
