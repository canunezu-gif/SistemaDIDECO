import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from config import *

class InventarioView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Filtros
        self.filtros = {
            "codigo": "", "descripcion": "", "anio": "", "depto": "", 
            "oc": "", "seccion": "", "direccion": "", "proceso": "", 
            "stock": "Todos", "pmin": "", "pmax": ""
        }

        self.configurar_estilo_tabla()
        self.setup_ui()
        self.cargar_datos()

    def configurar_estilo_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Estilo para que parezca una tabla moderna y no antigua
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        rowheight=35,
                        fieldbackground="white",
                        font=("Arial", 10),
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background="#E2E8F0", 
                        foreground="#1E293B", 
                        font=("Arial", 10, "bold"),
                        relief="flat")
        
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

    def setup_ui(self):
        # Header (Sin margen superior excesivo)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=(10, 5))
        
        ctk.CTkLabel(head, text="Mantenedor de Inventario", font=("Arial", 26, "bold"), text_color=COLOR_SIDEBAR).pack(side="left")
        
        # Botones
        btns = ctk.CTkFrame(head, fg_color="transparent")
        btns.pack(side="right")
        self.btn_sync = ctk.CTkButton(btns, text="↻ Sincronizar", fg_color="white", text_color=COLOR_SIDEBAR, border_width=1, width=120, command=self.sincronizar_datos)
        self.btn_sync.pack(side="left", padx=5)
        ctk.CTkButton(btns, text="📊 Excel", fg_color="#10B981", width=80, command=self.exportar_excel).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="📜 SQL", fg_color="#3B82F6", width=80, command=self.ver_sql).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="+ Nuevo", fg_color=COLOR_SIDEBAR, width=100, command=self.abrir_modal).pack(side="left", padx=5)

        # Barra Filtros
        bar = ctk.CTkFrame(self, fg_color="white", height=60, corner_radius=10)
        bar.pack(fill="x", padx=30, pady=(5, 10))
        
        ctk.CTkLabel(bar, text="Búsqueda Rápida:").pack(side="left", padx=(20, 5))
        self.entry_search = ctk.CTkEntry(bar, placeholder_text="Código o Descripción...", width=300, border_color="#E2E8F0")
        self.entry_search.pack(side="left", padx=5, pady=10)
        self.entry_search.bind("<Return>", lambda e: self.cargar_datos())
        
        ctk.CTkButton(bar, text="🔍", width=40, fg_color=COLOR_SIDEBAR, command=self.cargar_datos).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="X", width=40, fg_color="#94A3B8", command=self.limpiar_filtros).pack(side="left", padx=5)
        
        ctk.CTkButton(bar, text="Filtros Avanzados ▾", fg_color="transparent", text_color="#475569", 
                      border_width=1, border_color="#CBD5E1", command=self.abrir_filtros_avanzados).pack(side="right", padx=20)

        # --- TABLA (Aquí arreglamos el acomodo) ---
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        cols = ("ID", "Codigo", "Descripcion", "Anio", "Depto", "OC", "Stock", "Precio")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        # Configuración de Columnas para que se vean bien
        # stretch=True hace que ocupen el espacio disponible
        self.tree.column("ID", width=0, stretch=False)
        self.tree.column("Codigo", width=120, anchor="w", stretch=False)
        self.tree.column("Descripcion", width=400, anchor="w", stretch=True) # Descripción se estira más
        self.tree.column("Anio", width=60, anchor="center", stretch=False)
        self.tree.column("Depto", width=100, anchor="center", stretch=False)
        self.tree.column("OC", width=120, anchor="w", stretch=False)
        self.tree.column("Stock", width=80, anchor="center", stretch=False)
        self.tree.column("Precio", width=100, anchor="e", stretch=False)
        
        # Encabezados
        self.tree.heading("Codigo", text="CÓDIGO")
        self.tree.heading("Descripcion", text="DESCRIPCIÓN")
        self.tree.heading("Anio", text="AÑO")
        self.tree.heading("Depto", text="DEPTO")
        self.tree.heading("OC", text="OC INTERNA")
        self.tree.heading("Stock", text="STOCK")
        self.tree.heading("Precio", text="PRECIO")
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Menú Contextual
        self.menu_contextual = tk.Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="Eliminar", command=self.borrar_seleccionado)
        self.tree.bind("<Button-3>", self.mostrar_menu)

        # Footer Stats
        self.lbl_stats = ctk.CTkLabel(self, text="Total items: 0", font=("Arial", 11), text_color="gray")
        self.lbl_stats.pack(side="bottom", anchor="e", padx=30, pady=5)
        
        # Tags de color
        self.tree.tag_configure('critico', background='#FEF3C7')
        self.tree.tag_configure('vacio', background='#FEE2E2')

    def cargar_datos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        sql = "SELECT id, codigo, obs_linea, anio, departamento, oc_interna, stock, precio_compra FROM inventario WHERE 1=1"
        p = []
        
        txt = self.entry_search.get()
        if txt:
            sql += " AND (codigo LIKE ? OR obs_linea LIKE ?)"
            p.extend([f"%{txt}%", f"%{txt}%"])
            
        # Filtros Avanzados
        if self.filtros["anio"]:
            sql += " AND CAST(anio AS TEXT) LIKE ?"
            p.append(f"%{self.filtros['anio']}%")
        if self.filtros["descripcion"]:
            sql += " AND obs_linea LIKE ?"
            p.append(f"%{self.filtros['descripcion']}%")
        if self.filtros["codigo"]:
            sql += " AND codigo LIKE ?"
            p.append(f"%{self.filtros['codigo']}%")
        if self.filtros["depto"]: 
            sql += " AND departamento LIKE ?"
            p.append(f"%{self.filtros['depto']}%")
        if self.filtros["oc"]: 
            sql += " AND oc_interna LIKE ?"
            p.append(f"%{self.filtros['oc']}%")
            
        if self.filtros["stock"] == "Crítico": 
            sql += " AND stock <= 5 AND stock > 0"
        elif self.filtros["stock"] == "Sin Stock": 
            sql += " AND stock = 0"
            
        rows = self.db.fetch(sql, tuple(p))
        
        for r in rows:
            uid, c, d, a, dep, oc, stk, pr = r
            try: pr_fmt = f"${pr:,.0f}".replace(",", ".")
            except: pr_fmt = str(pr)
            
            tag = ()
            if stk == 0: tag = ('vacio',)
            elif stk <= 5: tag = ('critico',)
            
            self.tree.insert("", "end", values=(uid, c, d, a, dep, oc, stk, pr_fmt), tags=tag)
            
        self.lbl_stats.configure(text=f"Total items: {len(rows)}")

    def abrir_filtros_avanzados(self):
        t = ctk.CTkToplevel(self)
        t.title("Filtros Avanzados")
        t.geometry("600x550")
        f = ctk.CTkFrame(t, fg_color="white"); f.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(f, text="Búsqueda Detallada", font=("Arial", 16, "bold"), text_color=COLOR_SIDEBAR).pack(pady=(0,20))
        
        grid = ctk.CTkFrame(f, fg_color="transparent"); grid.pack(fill="x")
        inputs = {}
        campos = [
            ("Año", "anio", 0, 0), ("Descripción", "descripcion", 0, 1), 
            ("Código", "codigo", 1, 0), ("Departamento", "depto", 1, 1),
            ("Orden Compra", "oc", 2, 0)
        ]
        
        for lbl, key, r, c in campos:
            ctk.CTkLabel(grid, text=lbl, font=("Arial",11,"bold")).grid(row=r*2, column=c, sticky="w", padx=10, pady=(5,0))
            e = ctk.CTkEntry(grid, width=200); e.grid(row=r*2+1, column=c, sticky="w", padx=10, pady=(0,10))
            e.insert(0, self.filtros[key])
            inputs[key] = e
            
        ctk.CTkLabel(grid, text="Estado Stock", font=("Arial",11,"bold")).grid(row=8, column=0, sticky="w", padx=10)
        cb = ctk.CTkComboBox(grid, values=["Todos", "Disponible", "Crítico", "Sin Stock"])
        cb.set(self.filtros["stock"])
        cb.grid(row=9, column=0, sticky="w", padx=10)
        
        def aplicar():
            for key in inputs: self.filtros[key] = inputs[key].get()
            self.filtros["stock"] = cb.get()
            self.cargar_datos()
            t.destroy()
            
        def limpiar_modal():
            for key in inputs: inputs[key].delete(0, 'end')
            cb.set("Todos")
            
        btn_box = ctk.CTkFrame(f, fg_color="transparent")
        btn_box.pack(side="bottom", fill="x", pady=20)
        ctk.CTkButton(btn_box, text="Limpiar Campos", fg_color="gray", command=limpiar_modal).pack(side="left", padx=10, expand=True)
        ctk.CTkButton(btn_box, text="Aplicar Filtros", fg_color=COLOR_SIDEBAR, command=aplicar).pack(side="left", padx=10, expand=True)

    def limpiar_filtros(self):
        self.entry_search.delete(0, 'end')
        for key in self.filtros: self.filtros[key] = ""
        self.filtros["stock"] = "Todos"
        self.cargar_datos()

    def sincronizar_datos(self):
        self.btn_sync.configure(state="disabled", text="Conectando...")
        self.update_idletasks()
        exito, msg = self.db.sincronizar_con_sqlserver()
        self.btn_sync.configure(state="normal", text="↻ Sincronizar")
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)

    def exportar_excel(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if f:
            data = [self.tree.item(i)['values'] for i in self.tree.get_children()]
            df = pd.DataFrame(data, columns=["ID", "COD", "DESC", "ANIO", "DEPTO", "OC", "STOCK", "PRECIO"])
            df.drop("ID", axis=1, inplace=True)
            df.to_excel(f, index=False)
            messagebox.showinfo("Listo", "Excel exportado")

    def ver_sql(self):
        script = f"-- Exportación Inventario DIDECO\n-- Fecha: {datetime.now()}\n\nBEGIN TRANSACTION;\n"
        items = self.tree.get_children()
        for item in items:
            v = self.tree.item(item)['values']
            pr = str(v[7]).replace("$", "").replace(".", "")
            de = str(v[2]).replace("'", "''") 
            script += f"INSERT INTO Inventario (Cod, Desc, Stock, Precio) VALUES ('{v[1]}', '{de}', {v[6]}, {pr});\n"
        script += "COMMIT;"
        
        t = ctk.CTkToplevel(self)
        t.title("SQL Generado")
        t.geometry("600x500")
        txt = ctk.CTkTextbox(t, font=("Consolas", 12))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("0.0", script)

    def mostrar_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu_contextual.post(event.x_root, event.y_root)

    def borrar_seleccionado(self):
        sel = self.tree.selection()
        if not sel: return
        uid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar del inventario local?"):
            self.db.execute("DELETE FROM inventario WHERE id=?", (uid,))
            self.cargar_datos()

    def abrir_modal(self):
        t = ctk.CTkToplevel(self)
        t.title("Nuevo Producto Manual")
        t.geometry("600x650")
        f = ctk.CTkScrollableFrame(t, fg_color="white")
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        campos = ["Codigo", "Año", "Proceso", "Descripción", "Departamento", "Seccion", "OC Interna", "Stock", "Precio"]
        entries = {}
        for c in campos:
            ctk.CTkLabel(f, text=c, font=("Arial",11,"bold")).pack(anchor="w")
            e = ctk.CTkEntry(f); e.pack(fill="x", pady=5)
            entries[c] = e
            
        def guardar():
            try:
                vals = (
                    entries["Codigo"].get(),
                    int(entries["Año"].get() or 2024),
                    entries["Proceso"].get(),
                    entries["Descripción"].get(),
                    "Manual", 
                    entries["Departamento"].get(),
                    entries["Seccion"].get(),
                    int(entries["Precio"].get() or 0),
                    entries["OC Interna"].get(),
                    "S/I", 
                    str(datetime.now().date()),
                    int(entries["Stock"].get() or 0),
                    int(entries["Stock"].get() or 0)
                )
                sql = """INSERT INTO inventario (codigo, anio, proceso, obs_linea, direccion, departamento, seccion, 
                         precio_compra, oc_interna, oc_mercado_publico, fecha_subida, cantidad_comprada, stock)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                
                if self.db.execute(sql, vals):
                    t.destroy(); self.cargar_datos()
                else:
                    messagebox.showerror("Error", "Código duplicado")
            except Exception as e: messagebox.showerror("Error", str(e))
            
        ctk.CTkButton(f, text="Guardar", command=guardar, fg_color=COLOR_SIDEBAR).pack(pady=20)