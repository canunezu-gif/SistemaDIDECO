import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from collections import Counter
from config import *

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.fig_barras = None; self.fig_dona = None
        
        # TÍTULO SUBIDO (pady reducido)
        ctk.CTkLabel(self, text="Dashboard DIDECO", font=("Arial", 28, "bold"), text_color=COLOR_SIDEBAR).pack(pady=(10,5), padx=20, anchor="w")
        ctk.CTkLabel(self, text="Resumen estratégico.", font=("Arial", 12), text_color="gray").pack(padx=20, anchor="w", pady=(0,10))
        
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=10, pady=5)
        self.cargar_kpis()

        self.charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.charts_frame.grid_columnconfigure(0, weight=2)
        self.charts_frame.grid_columnconfigure(1, weight=1)
        
        self.crear_grafico_entregas(self.charts_frame)
        self.crear_grafico_tipos(self.charts_frame)

    def cargar_kpis(self):
        try:
            n_ayudas = len(self.db.fetch("SELECT * FROM entregas"))
            n_beneficiarios = len(self.db.fetch("SELECT * FROM beneficiarios"))
            res_stock = self.db.fetch("SELECT SUM(stock) FROM inventario")
            n_stock = res_stock[0][0] if res_stock and res_stock[0][0] else 0
            n_criticos = len(self.db.fetch("SELECT * FROM inventario WHERE stock <= 5"))
        except: n_ayudas = n_beneficiarios = n_stock = n_criticos = 0

        self.card(self.kpi_frame, "Total Ayudas", str(n_ayudas), "Entregas", 0)
        self.card(self.kpi_frame, "Beneficiarios", str(n_beneficiarios), "Activos", 1)
        self.card(self.kpi_frame, "Inventario", str(n_stock), "Unidades", 2)
        self.card(self.kpi_frame, "Stock Crítico", str(n_criticos), "Reponer", 3, is_alert=True)

    def card(self, parent, title, value, footer, col, is_alert=False):
        color_val = "#DC2626" if is_alert else COLOR_SIDEBAR
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=120)
        card.pack(side="left", expand=True, fill="x", padx=10)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), text_color="#64748B").place(x=20, y=15)
        ctk.CTkLabel(card, text=value, font=("Arial", 32, "bold"), text_color=color_val).place(x=20, y=40)
        ctk.CTkLabel(card, text=footer, font=("Arial", 10), text_color="#94A3B8").place(x=20, y=85)

    def crear_grafico_entregas(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Evolución de Entregas", font=("Arial", 14, "bold"), text_color="#1E293B").pack(pady=10)
        try:
            rows = self.db.fetch("SELECT fecha FROM entregas")
            fechas = [r[0] for r in rows]
            conteo = Counter(fechas)
            fechas_ord = sorted(conteo.keys(), key=lambda x: datetime.strptime(x, "%d-%m-%Y") if x else datetime.now())
            valores = [conteo[f] for f in fechas_ord]
            if not fechas_ord: fechas_ord, valores = ["Sin Datos"], [0]
        except: fechas_ord, valores = ["Error"], [0]

        self.fig_barras, ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.fig_barras.patch.set_facecolor('white')
        ax.bar(fechas_ord[-7:], valores[-7:], color="#3B82F6", alpha=0.8, width=0.5)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        canvas = FigureCanvasTkAgg(self.fig_barras, master=frame)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def crear_grafico_tipos(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Categorías", font=("Arial", 14, "bold"), text_color="#1E293B").pack(pady=10)
        try:
            rows = self.db.fetch("SELECT tipo_ayuda FROM entregas")
            tipos = [r[0] for r in rows]
            conteo = Counter(tipos)
            if not conteo: labels, sizes = ["Sin Datos"], [1]
            else: labels, sizes = list(conteo.keys()), list(conteo.values())
        except: labels, sizes = ["Error"], [1]

        self.fig_dona, ax = plt.subplots(figsize=(4, 4), dpi=100)
        self.fig_dona.patch.set_facecolor('white')
        ax.pie(sizes, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        self.fig_dona.gca().add_artist(plt.Circle((0,0),0.70,fc='white'))
        ax.legend(labels, loc="center", bbox_to_anchor=(0.5, -0.1), fontsize=8, frameon=False)
        canvas = FigureCanvasTkAgg(self.fig_dona, master=frame)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def destroy(self):
        if self.fig_barras: plt.close(self.fig_barras)
        if self.fig_dona: plt.close(self.fig_dona)
        super().destroy()