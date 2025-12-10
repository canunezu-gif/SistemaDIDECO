import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime
from config import *
from utils.pdf_generator import generar_ticket

class AyudasView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Título
        ctk.CTkLabel(self, text="Gestión de Ayudas Sociales", font=("Arial", 28, "bold"), text_color=COLOR_SIDEBAR).pack(pady=20, padx=30, anchor="w")
        
        # Layout Principal
        main_grid = ctk.CTkFrame(self, fg_color="transparent")
        main_grid.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- COLUMNA IZQUIERDA: FORMULARIO ---
        form = ctk.CTkFrame(main_grid, fg_color="white", corner_radius=10)
        form.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        ctk.CTkLabel(form, text="Registro de Entrega", font=("Arial", 18, "bold"), text_color=COLOR_SIDEBAR).pack(anchor="w", padx=30, pady=25)
        
        # 1. Buscador de Beneficiario
        row_rut = ctk.CTkFrame(form, fg_color="transparent")
        row_rut.pack(fill="x", padx=30, pady=(0, 10))
        
        self.entry_rut = ctk.CTkEntry(row_rut, placeholder_text="RUT Beneficiario (Ej: 12.345.678-9)", height=40)
        self.entry_rut.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(row_rut, text="🔍 Buscar", width=100, height=40, fg_color=COLOR_SIDEBAR, command=self.buscar_beneficiario).pack(side="left")
        
        # Info Beneficiario
        self.lbl_nombre = ctk.CTkLabel(form, text="Nombre: -", font=("Arial", 12), text_color="gray", anchor="w")
        self.lbl_nombre.pack(fill="x", padx=35, pady=0)
        
        self.lbl_direccion = ctk.CTkLabel(form, text="Dirección: -", font=("Arial", 12), text_color="gray", anchor="w")
        self.lbl_direccion.pack(fill="x", padx=35, pady=(0, 20))
        
        ctk.CTkFrame(form, height=2, fg_color="#F1F5F9").pack(fill="x", padx=30, pady=10)
        
        # 2. Datos de la Ayuda
        grid_datos = ctk.CTkFrame(form, fg_color="transparent")
        grid_datos.pack(fill="x", padx=30, pady=10)
        
        # Fila 1: Fecha (Editable) y Tipo
        ctk.CTkLabel(grid_datos, text="Fecha Entrega", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_fecha = ctk.CTkEntry(grid_datos, height=35)
        self.entry_fecha.insert(0, datetime.now().strftime("%d-%m-%Y")) # Fecha hoy por defecto
        self.entry_fecha.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        ctk.CTkLabel(grid_datos, text="Tipo de Ayuda", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w", pady=5)
        # Cargar categorías desde BD
        cats = [c[0] for c in self.db.fetch("SELECT nombre FROM categorias_ayuda")]
        self.cb_tipo = ctk.CTkComboBox(grid_datos, values=cats if cats else ["General"], width=250, height=35)
        self.cb_tipo.grid(row=1, column=1, sticky="ew", pady=(0, 15))
        
        # Fila 2: Producto y Cantidad
        ctk.CTkLabel(grid_datos, text="Producto (Inventario)", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.cb_producto = ctk.CTkComboBox(grid_datos, values=self.cargar_productos_inventario(), width=250, height=35, command=self.al_seleccionar_producto)
        self.cb_producto.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        ctk.CTkLabel(grid_datos, text="Cantidad", font=("Arial", 12, "bold")).grid(row=2, column=1, sticky="w", pady=5)
        self.entry_cant = ctk.CTkEntry(grid_datos, placeholder_text="1", height=35)
        self.entry_cant.grid(row=3, column=1, sticky="ew", pady=(0, 15))
        
        # Fila 3: Valor (Editable)
        ctk.CTkLabel(grid_datos, text="Valor Unitario ($)", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_valor = ctk.CTkEntry(grid_datos, placeholder_text="0", height=35)
        self.entry_valor.grid(row=5, column=0, sticky="ew", padx=(0,10), pady=(0, 15))

        # Detalle y Quien Retira
        ctk.CTkLabel(form, text="Detalle (Prescrito por Profesional)", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
        self.entry_detalle = ctk.CTkEntry(form, height=35)
        self.entry_detalle.pack(fill="x", padx=30, pady=(5, 15))
        
        ctk.CTkLabel(form, text="Quien Retira (Nombre Completo)", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
        self.entry_retira = ctk.CTkEntry(form, height=35)
        self.entry_retira.pack(fill="x", padx=30, pady=(5, 25))
        
        # Botón Guardar
        ctk.CTkButton(form, text="💾 Generar Comprobante", height=50, fg_color=COLOR_SIDEBAR, 
                      font=("Arial", 14, "bold"), command=self.guardar_entrega).pack(fill="x", padx=30, side="bottom", pady=30)

        # --- COLUMNA DERECHA: PREVIEW ---
        preview = ctk.CTkFrame(main_grid, fg_color="#ECFDF5", width=300, corner_radius=10)
        preview.pack(side="right", fill="y")
        preview.pack_propagate(False)
        
        ctk.CTkLabel(preview, text="Vista Previa", font=("Arial", 14, "bold"), text_color="#065F46").pack(pady=30)
        
        # Mockup visual simple
        ticket = ctk.CTkFrame(preview, fg_color="white", width=220, height=300)
        ticket.pack(pady=10)
        msg = "MUNICIPALIDAD\n\nComprobante de Entrega\n\n----------------\nRUT: ...\nBeneficio: ...\n----------------\n\n\nFirma"
        ctk.CTkLabel(ticket, text=msg, font=("Courier", 10), justify="center").place(relx=0.5, rely=0.5, anchor="center")

    def cargar_productos_inventario(self):
        try:
            data = self.db.fetch("SELECT codigo, obs_linea, stock, precio_compra FROM inventario WHERE stock > 0")
            if not data: return ["Sin Stock Disponible"]
            self.productos_data = {f"{d[1]} (Stock: {d[2]})": d[3] for d in data} # Guardar precio en memoria
            return list(self.productos_data.keys())
        except: return []

    def al_seleccionar_producto(self, choice):
        # Auto-completar precio si existe en memoria
        if hasattr(self, 'productos_data') and choice in self.productos_data:
            precio = self.productos_data[choice]
            self.entry_valor.delete(0, 'end')
            self.entry_valor.insert(0, str(precio))

    def buscar_beneficiario(self):
        rut = self.entry_rut.get()
        res = self.db.fetch("SELECT nombres, ap_paterno, ap_materno, direccion FROM beneficiarios WHERE rut=?", (rut,))
        
        if res:
            nombre = f"{res[0][0]} {res[0][1]} {res[0][2]}"
            direccion = res[0][3]
            self.lbl_nombre.configure(text=f"Nombre: {nombre}", text_color=COLOR_SIDEBAR)
            self.lbl_direccion.configure(text=f"Dirección: {direccion}")
        else:
            messagebox.showwarning("No encontrado", "RUT no registrado. Regístrelo en Beneficiarios.")

    def guardar_entrega(self):
        if "Nombre: -" in self.lbl_nombre.cget("text"):
            return messagebox.showerror("Error", "Seleccione un beneficiario válido.")
        
        folio = str(self.db.get_folio()).zfill(6)
        rut_ben = self.entry_rut.get()
        nombre_ben = self.lbl_nombre.cget("text").replace("Nombre: ", "")
        direccion_ben = self.lbl_direccion.cget("text").replace("Dirección: ", "")
        prod_full = self.cb_producto.get()
        prod_clean = prod_full.split(" (Stock")[0]
        
        datos = {
            'folio': folio,
            'fecha': self.entry_fecha.get(), # FECHA EDITABLE
            'rut': rut_ben,
            'nombres': nombre_ben,
            'direccion': direccion_ben,
            'tipo': self.cb_tipo.get(),
            'producto': prod_clean,
            'cant': self.entry_cant.get(),
            'valor': self.entry_valor.get(),
            'detalle': self.entry_detalle.get(),
            'retira': self.entry_retira.get()
        }
        
        sql = "INSERT INTO entregas (rut_beneficiario, fecha, tipo_ayuda, producto, cantidad, valor, detalle, quien_retira) VALUES (?,?,?,?,?,?,?,?)"
        if self.db.execute(sql, (datos['rut'], datos['fecha'], datos['tipo'], datos['producto'], datos['cant'], datos['valor'], datos['detalle'], datos['retira'])):
            
            # Descontar Stock
            try:
                self.db.execute("UPDATE inventario SET stock = stock - ? WHERE obs_linea = ?", (int(datos['cant']), prod_clean))
            except: pass
            
            generar_ticket(datos)
            messagebox.showinfo("Éxito", f"Entrega registrada. Folio: {folio}")
            self.entry_rut.delete(0, 'end'); self.lbl_nombre.configure(text="Nombre: -"); self.lbl_direccion.configure(text="Dirección: -")
        else:
            messagebox.showerror("Error", "Error al guardar en BD")