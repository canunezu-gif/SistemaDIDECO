import customtkinter as ctk
from tkinter import messagebox, filedialog
import csv
from config import *

class ReportesView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Título
        ctk.CTkLabel(self, text="Reportes y Listados", font=("Arial", 28, "bold"), text_color=COLOR_SIDEBAR).pack(pady=20, padx=30, anchor="w")
        
        # Contenedor de Botones Grandes
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=20)
        
        # Botón 1: Inventario General
        self.crear_boton_reporte(grid, "📦 Inventario General", 
                                 "Listado completo de productos en bodega con su valorización y stock actual.", 
                                 "Inventario.csv", "SELECT * FROM inventario", "#EFF6FF", "#1D4ED8")
                                 
        # Botón 2: Stock Crítico
        self.crear_boton_reporte(grid, "⚠️ Productos sin Stock", 
                                 "Listado filtrado solo con productos que tienen stock 0 o bajo el mínimo.", 
                                 "Stock_Critico.csv", "SELECT * FROM inventario WHERE stock <= 5", "#FEF2F2", "#B91C1C")
                                 
        # Botón 3: Historial Entregas
        self.crear_boton_reporte(grid, "📋 Historial de Entregas", 
                                 "Reporte detallado por fecha, profesional y beneficiario para auditoría.", 
                                 "Ayudas_Entregadas.csv", "SELECT * FROM entregas", "#F0FDF4", "#15803D")

    def crear_boton_reporte(self, parent, titulo, desc, filename, query, bg_color, text_color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, border_color="#E2E8F0", border_width=1)
        card.pack(side="left", expand=True, fill="both", padx=10)
        
        # Header Colorido
        header = ctk.CTkFrame(card, fg_color=bg_color, height=6, corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(card, text=titulo, font=("Arial", 16, "bold"), text_color=text_color).pack(pady=(20, 10), padx=20, anchor="w")
        ctk.CTkLabel(card, text=desc, font=("Arial", 12), text_color="gray", wraplength=250, justify="left").pack(pady=(0, 20), padx=20, anchor="w")
        
        ctk.CTkButton(card, text="⬇ Descargar Excel", fg_color="white", border_color=text_color, border_width=1, text_color=text_color,
                      hover_color=bg_color, command=lambda: self.exportar_csv(filename, query)).pack(side="bottom", pady=20, padx=20, fill="x")

    def exportar_csv(self, filename, query):
        try:
            rows = self.db.fetch(query)
            if not rows:
                return messagebox.showinfo("Información", "No hay datos disponibles para generar este reporte.")
                
            file_path = filedialog.asksaveasfilename(initialfile=filename, defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")])
            
            if file_path:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Opcional: Escribir cabeceras si las tuviéramos definidas, aquí van los datos raw
                    writer.writerows(rows)
                messagebox.showinfo("Éxito", f"Archivo guardado correctamente en:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}")