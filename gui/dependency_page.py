import customtkinter as ctk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DependencyPage(ctk.CTkFrame):
    def __init__(self, master, engine, nav_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.nav_callback = nav_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(self, text="Dependency Management", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")
        
        # Left Panel - Add Dependencies
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        
        ctk.CTkLabel(self.left_panel, text="Add New Dependency", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        # Dropdowns for tasks
        self.task_list = []
        
        ctk.CTkLabel(self.left_panel, text="Predecessor Task (Runs First):").pack(pady=(10, 5))
        self.pred_var = ctk.StringVar()
        self.pred_dropdown = ctk.CTkOptionMenu(self.left_panel, variable=self.pred_var, values=["Select Task"])
        self.pred_dropdown.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.left_panel, text="Successor Task (Must Wait):").pack(pady=(10, 5))
        self.succ_var = ctk.StringVar()
        self.succ_dropdown = ctk.CTkOptionMenu(self.left_panel, variable=self.succ_var, values=["Select Task"])
        self.succ_dropdown.pack(pady=5, padx=20, fill="x")
        
        add_btn = ctk.CTkButton(self.left_panel, text="Add Dependency", command=self.add_dependency)
        add_btn.pack(pady=30, padx=20, fill="x")

        # Right Panel - Graph Visualization
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        
        ctk.CTkLabel(self.right_panel, text="Dependency Graph", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Canvas for matplotlib
        self.canvas_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.canvas_frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.canvas = None

    def update_data(self):
        """Called when page is opened to refresh task list and graph."""
        self.task_list = list(self.engine.tasks.keys())
        if not self.task_list:
            self.pred_dropdown.configure(values=["No tasks available"])
            self.succ_dropdown.configure(values=["No tasks available"])
            self.pred_var.set("No tasks available")
            self.succ_var.set("No tasks available")
        else:
            self.pred_dropdown.configure(values=self.task_list)
            self.succ_dropdown.configure(values=self.task_list)
            self.pred_var.set(self.task_list[0])
            if len(self.task_list) > 1:
                self.succ_var.set(self.task_list[1])
            else:
                self.succ_var.set(self.task_list[0])
                
        self.draw_graph()

    def add_dependency(self):
        pred = self.pred_var.get()
        succ = self.succ_var.get()
        
        if pred not in self.task_list or succ not in self.task_list:
            messagebox.showerror("Error", "Please select valid tasks.")
            return
            
        if pred == succ:
            messagebox.showerror("Error", "A task cannot depend on itself.")
            return
            
        try:
            self.engine.dag_manager.add_dependency(pred, succ)
            messagebox.showinfo("Success", f"Dependency added: {pred} -> {succ}")
            self.draw_graph()
        except ValueError as e:
            messagebox.showerror("Cycle Detected", str(e))

    def draw_graph(self):
        # Clear old canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        # Apply dark mode aesthetics roughly based on CustomTkinter mode
        mode = ctk.get_appearance_mode()
        bg_color = '#2b2b2b' if mode == 'Dark' else '#f0f0f0'
        text_color = 'white' if mode == 'Dark' else 'black'
        
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        
        G = nx.DiGraph()
        
        # Add all tasks as nodes
        for t_id in self.engine.tasks:
            G.add_node(t_id)
            
        # Add edges
        for u, neighbors in self.engine.dag_manager.adj_list.items():
            for v in neighbors:
                G.add_edge(u, v)
                
        if len(G.nodes) > 0:
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, ax=ax, with_labels=True, node_color='#1f538d', 
                    font_color='white', node_size=1500, font_weight='bold', 
                    edge_color=text_color, arrows=True, arrowsize=20)
        else:
            ax.text(0.5, 0.5, 'No tasks to display', 
                    horizontalalignment='center', verticalalignment='center',
                    color=text_color, transform=ax.transAxes)
            
        ax.axis('off')
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill="both")
