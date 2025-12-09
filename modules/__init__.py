import customtkinter as ctk
from config import *

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 28, "bold"), text_color=COLOR_SIDEBAR).pack(pady=20, padx=30, anchor="w")
        
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=30)
        
        # Datos Reales
        n_ayudas = len(self.db.fetch("SELECT * FROM entregas"))
        n_stock = self.db.fetch("SELECT SUM(stock) FROM inventario")[0][0] or 0
        n_ben = len(self.db.fetch("SELECT * FROM beneficiarios"))
        
        self.card(grid, "Ayudas Entregadas", str(n_ayudas), 0)
        self.card(grid, "Stock Total", str(n_stock), 1)
        self.card(grid, "Beneficiarios", str(n_ben), 2)

    def card(self, parent, title, val, col):
        f = ctk.CTkFrame(parent, fg_color="white", width=250, height=120)
        f.grid(row=0, column=col, padx=10, sticky="ew")
        ctk.CTkLabel(f, text=title, text_color="gray").pack(pady=(15,0))
        ctk.CTkLabel(f, text=val, font=("Arial", 30, "bold"), text_color=COLOR_SIDEBAR).pack()