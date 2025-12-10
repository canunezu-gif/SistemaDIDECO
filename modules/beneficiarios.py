import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
import os
import math
from config import *

class BeneficiariosView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # --- Variables de Paginación ---
        self.pagina_actual = 1
        self.registros_por_pagina = 50
        self.total_paginas = 1
        
        # Header
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(head, text="Gestor de Personas (Beneficiarios)", font=("Arial", 26, "bold"), text_color=COLOR_SIDEBAR).pack(side="left")
        
        # Botonera Superior
        btns = ctk.CTkFrame(head, fg_color="transparent")
        btns.pack(side="right")
        
        ctk.CTkButton(btns, text="📂 Importar RSH / Excel", fg_color="#10B981", text_color="white", command=self.importar_archivo).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="+ Nuevo Beneficiario", fg_color=COLOR_SIDEBAR, command=lambda: self.abrir_modal()).pack(side="left", padx=5)
        
        # Buscador
        search_fr = ctk.CTkFrame(self, fg_color="white")
        search_fr.pack(fill="x", padx=30)
        self.s_rut = ctk.CTkEntry(search_fr, width=300, placeholder_text="Buscar por RUT...")
        self.s_rut.pack(side="left", padx=20, pady=15)
        self.s_rut.bind("<Return>", lambda e: self.reiniciar_y_cargar()) # Enter para buscar
        ctk.CTkButton(search_fr, text="🔍", width=50, fg_color=COLOR_SIDEBAR, command=self.reiniciar_y_cargar).pack(side="left")
        
        # Headers Tabla
        h = ctk.CTkFrame(self, height=35, fg_color="#E2E8F0")
        h.pack(fill="x", padx=30, pady=(10,0))
        cols = ["RUT", "NOMBRES", "AP. PATERNO", "AP. MATERNO", "DIRECCIÓN", "TELÉFONO", "ACCIONES"]
        widths = [1, 2, 2, 2, 3, 1, 2] 
        for c, w in zip(cols, widths):
            ctk.CTkLabel(h, text=c, font=("Arial", 11, "bold")).pack(side="left", expand=True, fill="x", padx=2)

        # Tabla (Scrollable)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=5)
        
        # --- FOOTER CON PAGINACIÓN ---
        footer = ctk.CTkFrame(self, fg_color="transparent", height=50)
        footer.pack(fill="x", padx=30, pady=10)
        
        self.btn_prev = ctk.CTkButton(footer, text="< Anterior", width=100, command=self.pagina_anterior, state="disabled")
        self.btn_prev.pack(side="left")
        
        self.lbl_pag = ctk.CTkLabel(footer, text="Página 1 de 1", font=("Arial", 12, "bold"))
        self.lbl_pag.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(footer, text="Siguiente >", width=100, command=self.pagina_siguiente, state="disabled")
        self.btn_next.pack(side="right")

        # Cargar datos iniciales
        self.cargar()

    def reiniciar_y_cargar(self):
        """Reinicia a la página 1 cuando se hace una nueva búsqueda"""
        self.pagina_actual = 1
        self.cargar()

    def cargar(self):
        # Limpiar tabla visual
        for w in self.scroll.winfo_children(): w.destroy()
        
        # Preparar Query
        busqueda = self.s_rut.get().strip()
        filtro = f"%{busqueda}%"
        
        # 1. Contar total de registros para saber cuántas páginas hay
        sql_count = "SELECT COUNT(*) FROM beneficiarios WHERE rut LIKE ? OR nombres LIKE ? OR ap_paterno LIKE ?"
        total_items = self.db.fetch(sql_count, (filtro, filtro, filtro))[0][0]
        
        self.total_paginas = math.ceil(total_items / self.registros_por_pagina)
        if self.total_paginas == 0: self.total_paginas = 1
        
        # 2. Obtener solo los registros de la página actual (LIMIT y OFFSET)
        offset = (self.pagina_actual - 1) * self.registros_por_pagina
        sql_data = """SELECT id, rut, nombres, ap_paterno, ap_materno, direccion, telefono, email 
                      FROM beneficiarios 
                      WHERE rut LIKE ? OR nombres LIKE ? OR ap_paterno LIKE ?
                      ORDER BY id DESC 
                      LIMIT ? OFFSET ?"""
        
        rows = self.db.fetch(sql_data, (filtro, filtro, filtro, self.registros_por_pagina, offset))
        
        # 3. Renderizar filas
        for r in rows:
            uid, rut, nom, app, apm, dire, tel, mail = r
            c = ctk.CTkFrame(self.scroll, fg_color="white", height=45)
            c.pack(fill="x", pady=2)
            
            # Formato de texto para que no sea muy largo
            direccion_corta = (dire[:35] + '..') if len(dire) > 35 else dire
            
            values = [rut, nom, app, apm, direccion_corta, tel]
            for v in values:
                ctk.CTkLabel(c, text=v, font=("Arial", 11)).pack(side="left", expand=True, fill="x")

            btns = ctk.CTkFrame(c, fg_color="transparent")
            btns.pack(side="left", expand=True, fill="x")
            
            # Pasamos 'r' completo a abrir_modal para editar
            ctk.CTkButton(btns, text="✏️", width=30, fg_color="orange", command=lambda x=r: self.abrir_modal(x)).pack(side="left", padx=2)
            ctk.CTkButton(btns, text="🗑", width=30, fg_color=COLOR_DANGER, command=lambda x=uid: self.borrar(x)).pack(side="left", padx=2)

        # 4. Actualizar controles de paginación
        self.actualizar_controles()

    def actualizar_controles(self):
        self.lbl_pag.configure(text=f"Página {self.pagina_actual} de {self.total_paginas}")
        
        if self.pagina_actual == 1:
            self.btn_prev.configure(state="disabled", fg_color="gray")
        else:
            self.btn_prev.configure(state="normal", fg_color=COLOR_SIDEBAR)
            
        if self.pagina_actual == self.total_paginas:
            self.btn_next.configure(state="disabled", fg_color="gray")
        else:
            self.btn_next.configure(state="normal", fg_color=COLOR_SIDEBAR)

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.cargar()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar()

    def importar_archivo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv")])
        if not file_path: return

        try:
            if file_path.endswith('.csv'):
                try: df = pd.read_csv(file_path, encoding='latin-1', sep=None, engine='python')
                except: df = pd.read_csv(file_path, encoding='utf-8', sep=None, engine='python')
            else:
                df = pd.read_excel(file_path)
            
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            contador = 0
            
            for index, row in df.iterrows():
                try:
                    if 'run' in df.columns and 'dv' in df.columns:
                        rut = f"{row['run']}-{row['dv']}"
                    else:
                        rut = str(row.get('rut', '')).strip()

                    nom = str(row.get('nombres', '')).strip()
                    app = str(row.get('apellidopaterno', row.get('apellido paterno', ''))).strip()
                    apm = str(row.get('apellidomaterno', row.get('apellido materno', ''))).strip()

                    if 'n_calle_uni_rsh' in df.columns:
                        calle = str(row.get('n_calle_uni_rsh', '')).strip()
                        num = str(row.get('numdomicilio', '')).strip()
                        dire = f"{calle} {num}".strip()
                    else:
                        dire = str(row.get('dirección', row.get('direccion', ''))).strip()

                    tel = str(row.get('telefono', row.get('teléfono', ''))).strip()
                    mail = str(row.get('email', '')).strip()

                    if len(rut) > 2 and rut.lower() != 'nan-nan':
                        sql = """INSERT OR REPLACE INTO beneficiarios 
                                 (rut, nombres, ap_paterno, ap_materno, direccion, telefono, email) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
                        self.db.execute(sql, (rut, nom, app, apm, dire, tel, mail))
                        contador += 1
                except: pass

            messagebox.showinfo("Importación", f"Registros procesados: {contador}")
            self.reiniciar_y_cargar()

        except Exception as e:
            messagebox.showerror("Error", f"Detalle: {e}")

    def abrir_modal(self, data=None):
        t = ctk.CTkToplevel(self)
        t.geometry("700x550")
        t.title("Ficha Social" if data else "Nuevo Beneficiario")
        t.attributes("-topmost", True)
        
        f = ctk.CTkFrame(t, fg_color="white"); f.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(f, text="Datos Personales", font=("Arial", 18, "bold"), text_color=COLOR_SIDEBAR).pack(anchor="w", pady=15)
        
        grid = ctk.CTkFrame(f, fg_color="transparent"); grid.pack(fill="x")
        campos = [("RUT",0,0), ("Nombres",0,1), 
                  ("Apellido Paterno",1,0), ("Apellido Materno",1,1), 
                  ("Dirección",2,0), ("Teléfono",3,0), ("Email",3,1)]
        entries = {}
        for lbl, r, col in campos:
            ctk.CTkLabel(grid, text=lbl, font=("Arial", 11, "bold")).grid(row=r*2, column=col, sticky="w", padx=10, pady=(5,0))
            e = ctk.CTkEntry(grid, width=300)
            e.grid(row=r*2+1, column=col, padx=10, pady=(0,10))
            entries[lbl] = e
        
        if data:
            uid, rut, nom, app, apm, dire, tel, mail = data
            vals = {"RUT":rut, "Nombres":nom, "Apellido Paterno":app, "Apellido Materno":apm, 
                    "Dirección":dire, "Teléfono":tel, "Email":mail}
            for k, v in vals.items(): entries[k].insert(0, v)
            entries["RUT"].configure(state="disabled")

        def save():
            v = [entries[k].get() for k in ["RUT", "Nombres", "Apellido Paterno", "Apellido Materno", "Dirección", "Teléfono", "Email"]]
            if data:
                sql = "UPDATE beneficiarios SET nombres=?, ap_paterno=?, ap_materno=?, direccion=?, telefono=?, email=? WHERE rut=?"
                if self.db.execute(sql, v[1:] + [v[0]]):
                    t.destroy(); self.cargar(); messagebox.showinfo("OK", "Actualizado")
                else: messagebox.showerror("Error", "Error al actualizar")
            else:
                if self.db.execute("INSERT INTO beneficiarios (rut, nombres, ap_paterno, ap_materno, direccion, telefono, email) VALUES (?,?,?,?,?,?,?)", tuple(v)):
                    t.destroy(); self.reiniciar_y_cargar(); messagebox.showinfo("OK", "Creado")
                else: messagebox.showerror("Error", "RUT Duplicado")
            
        ctk.CTkButton(f, text="Guardar Ficha", fg_color=COLOR_SIDEBAR, height=45, command=save).pack(side="bottom", fill="x", pady=20)

    def borrar(self, uid):
        if messagebox.askyesno("Confirmar", "¿Eliminar beneficiario?"):
            self.db.execute("DELETE FROM beneficiarios WHERE id=?", (uid,))
            self.cargar()