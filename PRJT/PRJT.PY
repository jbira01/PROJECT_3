import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
from tkinter.font import Font

# Définition des couleurs et du thème
COLORS = {
    "primary": "#3498db",     # Bleu principal
    "primary_dark": "#2980b9", # Bleu foncé pour hover
    "secondary": "#2ecc71",   # Vert pour les actions positives
    "secondary_dark": "#27ae60", # Vert foncé pour hover
    "accent": "#e74c3c",      # Rouge pour les actions négatives/suppression
    "accent_dark": "#c0392b", # Rouge foncé pour hover
    "bg_light": "#f5f6fa",    # Fond clair
    "bg_dark": "#dfe6e9",     # Fond plus sombre pour contraste
    "text_dark": "#2d3436",   # Texte principal
    "text_light": "#ffffff",  # Texte sur fond coloré
    "completed": "#95a5a6"    # Gris pour les tâches terminées
}

class Task:
    
    def __init__(self, title, description="", due_date=None, completed=False):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = completed
    
    def to_dict(self):
        # Convert datetime to string for JSON serialization
        due_date_str = self.due_date.strftime("%Y-%m-%d") if self.due_date else None
        return {
            "title": self.title,
            "description": self.description,
            "due_date": due_date_str,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data):
        # Parse the due_date string back to a datetime object
        due_date_str = data.get("due_date")
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
        return cls(
            title=data["title"],
            description=data["description"],
            due_date=due_date,
            completed=data["completed"]
        )

# Widget personnalisé pour la sélection de date avec style amélioré
class DateEntry(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Variables to store day, month, and year
        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()
        
        # Get the current date
        current_date = datetime.now()
        
        # Set initial values to the current date
        self.day_var.set(str(current_date.day).zfill(2))
        self.month_var.set(str(current_date.month).zfill(2))
        self.year_var.set(str(current_date.year))
        
        # Labels and Comboboxes for day, month, and year with improved styling
        ttk.Label(self, text="Jour:", style="DateLabel.TLabel").grid(row=0, column=0, padx=2)
        self.day_combo = ttk.Combobox(self, textvariable=self.day_var, width=3, state="readonly", style="Date.TCombobox")
        self.day_combo.grid(row=0, column=1, padx=2)
        
        ttk.Label(self, text="Mois:", style="DateLabel.TLabel").grid(row=0, column=2, padx=2)
        self.month_combo = ttk.Combobox(self, textvariable=self.month_var, values=[str(i).zfill(2) for i in range(1, 13)], 
                                        width=3, state="readonly", style="Date.TCombobox")
        self.month_combo.grid(row=0, column=3, padx=2)
        self.month_combo.bind("<<ComboboxSelected>>", self.update_days)
        
        ttk.Label(self, text="Année:", style="DateLabel.TLabel").grid(row=0, column=4, padx=2)
        self.year_combo = ttk.Combobox(self, textvariable=self.year_var, values=[str(i) for i in range(2025, 2036)], 
                                       width=5, state="readonly", style="Date.TCombobox")
        self.year_combo.grid(row=0, column=5, padx=2)
        
        # Initialize days for the current month
        self.update_days()

    def update_days(self, event=None):
        month = int(self.month_var.get())
        
        # Number of days in each month
        if month == 2:  # February
            days_in_month = 28
        elif month in [4, 6, 9, 11]:  # April, June, September, November
            days_in_month = 30
        else:  # January, March, May, July, August, October, December
            days_in_month = 31
        
        # Update the day_combo values
        self.day_combo["values"] = [str(i).zfill(2) for i in range(1, days_in_month + 1)]
        
        # Ensure the selected day is within the valid range
        if int(self.day_var.get()) > days_in_month:
            self.day_var.set(str(days_in_month))
    
    def get_date(self):
        try:
            return datetime(int(self.year_var.get()), int(self.month_var.get()), int(self.day_var.get()))
        except ValueError:
            return datetime.now()
    
    def set_date(self, date_str):
        try:
            year, month, day = date_str.split("-")
            self.year_var.set(year)
            self.month_var.set(month.lstrip("0"))
            self.day_var.set(day.lstrip("0"))
        except Exception:
            pass

# Fenêtre modale pour ajouter ou modifier des tâches - design amélioré
class TaskDialog(tk.Toplevel):
    def __init__(self, parent, task=None, callback=None):
        super().__init__(parent)
        self.task = task
        self.callback = callback
        
        self.title("Ajouter une tâche" if task is None else "Modifier la tâche")
        self.geometry("450x350")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_light"])
        
        # Add some padding and styling
        self.main_frame = ttk.Frame(self, style="Dialog.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_widgets()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Set focus to title entry
        self.title_entry.focus_set()
    
    def create_widgets(self):
        # Title
        ttk.Label(self.main_frame, text="Titre:", style="DialogLabel.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.title_var = tk.StringVar(value=self.task.title if self.task else "")
        self.title_entry = ttk.Entry(self.main_frame, textvariable=self.title_var, width=30, style="Dialog.TEntry")
        self.title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Description
        ttk.Label(self.main_frame, text="Description:", style="DialogLabel.TLabel").grid(row=1, column=0, padx=10, pady=10, sticky="nw")
        self.description_text = tk.Text(self.main_frame, width=30, height=5, bg=COLORS["bg_light"], 
                                       fg=COLORS["text_dark"], font=("Segoe UI", 10), relief="flat",
                                       borderwidth=1, highlightthickness=1, highlightbackground=COLORS["bg_dark"])
        self.description_text.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        if self.task and self.task.description:
            self.description_text.insert("1.0", self.task.description)
        
        # Due Date
        ttk.Label(self.main_frame, text="Date limite:", style="DialogLabel.TLabel").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.due_date_entry = DateEntry(self.main_frame)
        self.due_date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        if self.task and self.task.due_date:
            self.due_date_entry.set_date(self.task.due_date.strftime("%Y-%m-%d"))
        
        # Buttons
        button_frame = ttk.Frame(self.main_frame, style="Dialog.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Enregistrer", command=self.save_task, style="Primary.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Annuler", command=self.destroy, style="Secondary.TButton").pack(side=tk.LEFT, padx=10)
    
    def save_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Erreur", "Le titre est obligatoire")
            return
        
        description = self.description_text.get("1.0", tk.END).strip()
        due_date = self.due_date_entry.get_date()
        
        if self.task:
            self.task.title = title
            self.task.description = description
            self.task.due_date = due_date
        else:
            self.task = Task(title, description, due_date)
        
        if self.callback:
            self.callback(self.task)
        self.destroy()

# Application principale avec interface utilisateur améliorée
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ma Liste de Tâches")
        self.geometry("900x650")
        self.configure(bg=COLORS["bg_light"])
        self.minsize(800, 600)
        
        # Override des configurations standard pour une meilleure visibilité des boutons
        self.option_add("*Button.Background", COLORS["bg_light"])
        self.option_add("*Button.foreground", "black")
        self.option_add("*Button.activeBackground", COLORS["bg_dark"])
        self.option_add("*Button.activeForeground", "black")
        self.option_add("*Button.highlightBackground", "black")
        self.option_add("*Button.highlightColor", "black")
        self.option_add("*Button.relief", "raised")
        
        self.tasks = []
        self.filename = "tasks.json"
        
        # Configuration des polices
        self.default_font = Font(family="Segoe UI", size=14)
        self.title_font = Font(family="Segoe UI", size=16, weight="bold")
        self.header_font = Font(family="Segoe UI", size=13, weight="bold")
        
        # Configuration des styles
        self.configure_styles()
        
        # Ajout d'un style spécifique aux boutons
        self.tk.call("tk", "scaling", 1.0)  # Ajustement de l'échelle pour une meilleure apparence
        
        # Création des widgets
        self.create_widgets()
        
        # Chargement des tâches
        self.load_tasks()
        
        # Centrer la fenêtre
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def configure_styles(self):
        self.style = ttk.Style()
        
        # Configuration générale
        self.style.configure(".", font=("Segoe UI", 12))
        self.style.configure("TFrame", background=COLORS["bg_light"])
        self.style.configure("Dialog.TFrame", background=COLORS["bg_light"])
        
        # Étiquettes
        self.style.configure("TLabel", background=COLORS["bg_light"], foreground=COLORS["text_dark"])
        self.style.configure("Title.TLabel", font=self.title_font, background=COLORS["bg_light"], foreground=COLORS["primary"])
        self.style.configure("DateLabel.TLabel", font=("Segoe UI", 13), background=COLORS["bg_light"])
        self.style.configure("DialogLabel.TLabel", font=("Segoe UI", 14, "bold"), background=COLORS["bg_light"])
        
        # Combobox
        self.style.map('TCombobox', fieldbackground=[('readonly', COLORS["bg_light"])])
        self.style.map('TCombobox', selectbackground=[('readonly', COLORS["primary"])])
        self.style.map('TCombobox', selectforeground=[('readonly', COLORS["text_light"])])
        
        # filter_tasks
        self.style.configure("Custom.TCombobox",
                            font=("Segoe UI", 20),
                            padding=5,
                            relief="solid",
                            borderwidth=1)
        self.style.map("Custom.TCombobox",
                    fieldbackground=[("readonly", COLORS["bg_light"])],
                    selectbackground=[("readonly", COLORS["primary"])],
                    selectforeground=[("readonly", COLORS["text_light"])])
        
        # Entrées
        self.style.configure("TEntry", fieldbackground=COLORS["bg_light"])
        self.style.configure("Dialog.TEntry", fieldbackground=COLORS["bg_light"])
        
        # Bouton principal (bleu)
        self.style.configure("Primary.TButton", 
                            font=("Segoe UI", 12, "bold"),
                            background=COLORS["primary"],
                            foreground="black")
        self.style.map("Primary.TButton",
                      background=[("active", COLORS["primary_dark"])],
                      foreground=[("active", "black")])
        
        # Bouton secondaire (gris)
        self.style.configure("Secondary.TButton", 
                            font=("Segoe UI", 12, "bold"),
                            background=COLORS["bg_dark"],
                            foreground="black")
        self.style.map("Secondary.TButton",
                      background=[("active", "#bdc3c7")],
                      foreground=[("active", "black")])
        
        # Bouton d'accent (rouge)
        self.style.configure("Accent.TButton", 
                            font=("Segoe UI", 12, "bold"),
                            background=COLORS["accent"],
                            foreground="black")
        self.style.map("Accent.TButton",
                      background=[("active", COLORS["accent_dark"])],
                      foreground=[("active", "black")])
        
        # Bouton vert
        self.style.configure("Green.TButton", 
                            font=("Segoe UI", 12, "bold"),
                            background=COLORS["secondary"],
                            foreground="black")
        self.style.map("Green.TButton",
                      background=[("active", COLORS["secondary_dark"])],
                      foreground=[("active", "black")])
        
        # Treeview
        self.style.configure("Treeview", 
                            background=COLORS["bg_light"],
                            foreground=COLORS["text_dark"],
                            rowheight=30,
                            fieldbackground=COLORS["bg_light"])
        self.style.configure("Treeview.Heading", 
                            font=self.header_font,
                            background=COLORS["bg_dark"],
                            foreground=COLORS["text_dark"])
        self.style.map("Treeview", background=[('selected', COLORS["primary"])], foreground=[('selected', COLORS["text_light"])])
    
    def create_widgets(self):
        # Conteneur principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre de l'application
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="Ma Liste de Tâches", style="Title.TLabel").pack(side=tk.LEFT)
        
        # Cadre de recherche et filtres
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Côté gauche - Recherche
        search_left = ttk.Frame(search_frame)
        search_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_left, text="Rechercher:", font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 15))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_tasks)
        search_entry = ttk.Entry(search_left, textvariable=self.search_var, width=30, font=("Segoe UI", 12))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Côté droit - Filtres
        search_right = ttk.Frame(search_frame)
        search_right.pack(side=tk.RIGHT)
        
        ttk.Label(search_right, text="Statut:", font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=5)
        self.status_filter = tk.StringVar(value="Tout")
        status_combo = ttk.Combobox(
            search_right, 
            textvariable=self.status_filter,
            font=("Segoe UI", 12),  
            values=["Tout", "En cours", "Terminé"],
            state="readonly",
            width=18, 
            style="Custom.TCombobox"  
        )
        status_combo.pack(side=tk.LEFT, padx=10, pady=2)
        status_combo.bind("<<ComboboxSelected>>", self.filter_tasks)
        
        # Cadre des boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Utilisation de boutons natifs Tk à la place de ttk pour un meilleur contrôle
        add_btn = tk.Button(button_frame, text="✚ Nouvelle tâche", 
                           command=self.add_task, 
                           bg=COLORS["primary"],
                           fg="black",
                           font=("Segoe UI", 12, "bold"),
                           relief="raised",
                           bd=2,
                           padx=10,
                           pady=3)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_btn = tk.Button(button_frame, text="✎ Modifier", 
                            command=self.edit_task, 
                            bg=COLORS["bg_dark"],
                            fg="black",
                            font=("Segoe UI", 12, "bold"),
                            relief="raised",
                            bd=2,
                            padx=10,
                            pady=3)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        status_btn = tk.Button(button_frame, text="✓ Changer statut", 
                              command=self.toggle_task_status, 
                              bg=COLORS["secondary"],
                              fg="black",
                              font=("Segoe UI", 12, "bold"),
                              relief="raised",
                              bd=2,
                              padx=10,
                              pady=3)
        status_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(button_frame, text="✕ Supprimer", 
                              command=self.delete_task, 
                              bg=COLORS["accent"],
                              fg="black",
                              font=("Segoe UI", 12, "bold"),
                              relief="raised",
                              bd=2,
                              padx=10,
                              pady=3)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Tableau des tâches
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Création du Treeview avec scrollbar
        self.task_tree = ttk.Treeview(table_frame, columns=("title", "description", "due_date", "status"), show="headings")
        self.task_tree.heading("title", text="Titre")
        self.task_tree.heading("description", text="Description")
        self.task_tree.heading("due_date", text="Date limite")
        self.task_tree.heading("status", text="Statut")
        
        # Ajustement des colonnes
        self.task_tree.column("title", width=200, minwidth=150)
        self.task_tree.column("description", width=350, minwidth=200)
        self.task_tree.column("due_date", width=120, minwidth=100)
        self.task_tree.column("status", width=120, minwidth=100)
        
        # Scrollbar vertical
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscroll=y_scrollbar.set)
        
        # Scrollbar horizontal
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.task_tree.xview)
        self.task_tree.configure(xscroll=x_scrollbar.set)
        
        # Placement des éléments
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Double-clic pour éditer
        self.task_tree.bind("<Double-1>", lambda event: self.edit_task())
        
        # Barre de statut
        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W, background=COLORS["bg_dark"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_tasks(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    task_dicts = json.load(f)
                    self.tasks = [Task.from_dict(task_dict) for task_dict in task_dicts]
                self.update_status_bar(f"{len(self.tasks)} tâches chargées")
            except Exception as e:
                messagebox.showerror("Erreur de chargement", f"Impossible de charger les tâches: {str(e)}")
        self.refresh_task_list()
    
    def save_tasks(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                task_dicts = [task.to_dict() for task in self.tasks]
                json.dump(task_dicts, f, indent=2, ensure_ascii=False)
            self.update_status_bar("Tâches enregistrées")
        except Exception as e:
            messagebox.showerror("Erreur d'enregistrement", f"Impossible d'enregistrer les tâches: {str(e)}")
    
    def add_task(self):
        def callback(task):
            self.tasks.append(task)
            self.refresh_task_list()
            self.save_tasks()
            self.update_status_bar("Nouvelle tâche ajoutée")
        
        TaskDialog(self, callback=callback)
    
    def edit_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Veuillez sélectionner une tâche à modifier")
            return
        
        task_index = int(selected_item[0])
        
        def callback(task):
            self.tasks[task_index] = task
            self.refresh_task_list()
            self.save_tasks()
            self.update_status_bar("Tâche mise à jour")
        
        TaskDialog(self, task=self.tasks[task_index], callback=callback)
    
    def delete_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Veuillez sélectionner une tâche à supprimer")
            return
        
        if not messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette tâche?"):
            return
        
        task_index = int(selected_item[0])
        del self.tasks[task_index]
        self.refresh_task_list()
        self.save_tasks()
        self.update_status_bar("Tâche supprimée")
    
    def toggle_task_status(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Veuillez sélectionner une tâche pour changer son statut")
            return
        
        task_index = int(selected_item[0])
        self.tasks[task_index].completed = not self.tasks[task_index].completed
        self.refresh_task_list()
        self.save_tasks()
        status = "terminée" if self.tasks[task_index].completed else "en cours"
        self.update_status_bar(f"Tâche marquée comme {status}")
    
    def refresh_task_list(self):
        # Effacer les données actuelles
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Obtenir les tâches filtrées
        filtered_tasks = self.get_filtered_tasks()
        
        # Réinsérer les données filtrées
        for task in filtered_tasks:
            status = "Terminé" if task.completed else "En cours"
            values = (task.title, 
                     task.description if len(task.description) < 50 else task.description[:47] + "...", 
                     task.due_date.strftime("%Y-%m-%d") if task.due_date else "", 
                     status)
            task_id = str(self.tasks.index(task))
            tags = ("completed",) if task.completed else ()
            self.task_tree.insert("", tk.END, iid=task_id, values=values, tags=tags)
        
        # Configurer les tags pour les tâches terminées
        self.task_tree.tag_configure("completed", foreground=COLORS["completed"])
    
    def search_tasks(self, *args):
        self.refresh_task_list()
    
    def filter_tasks(self, *args):
        self.refresh_task_list()
    
    def get_filtered_tasks(self):
        search_term = self.search_var.get().lower()
        status_filter = self.status_filter.get()
        
        filtered = self.tasks.copy()
        
        # Filtrer par terme de recherche
        if search_term:
            filtered = [task for task in filtered if search_term in task.title.lower() or search_term in task.description.lower()]
        
        # Filtrer par statut
        if status_filter == "En cours":
            filtered = [task for task in filtered if not task.completed]
        elif status_filter == "Terminé":
            filtered = [task for task in filtered if task.completed]
        
        return filtered
    
    def update_status_bar(self, message):
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()