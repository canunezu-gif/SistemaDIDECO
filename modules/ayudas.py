import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from config import *
from utils.pdf_generator import generar_ticket # Asegúrate de tener utils/pdf_generator.py

class AyudasView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Título
        ctk.CTkLabel(self, text="Gestión de Ayudas Sociales", font=("Arial", 28, "bold"), text_color=COLOR_SIDEBAR).pack(pady=20, padx=30, anchor="w")
        
        # Layout Principal (Izquierda Formulario, Derecha Preview)
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
        
        # Etiquetas de Info (Nombre y Dirección cargados automáticamente)
        self.lbl_nombre = ctk.CTkLabel(form, text="Nombre: -", font=("Arial", 12), text_color="gray", anchor="w")
        self.lbl_nombre.pack(fill="x", padx=35, pady=0)
        
        self.lbl_direccion = ctk.CTkLabel(form, text="Dirección: -", font=("Arial", 12), text_color="gray", anchor="w")
        self.lbl_direccion.pack(fill="x", padx=35, pady=(0, 20))
        
        # Separador
        ctk.CTkFrame(form, height=2, fg_color="#F1F5F9").pack(fill="x", padx=30, pady=10)
        
        # 2. Datos de la Ayuda
        grid_datos = ctk.CTkFrame(form, fg_color="transparent")
        grid_datos.pack(fill="x", padx=30, pady=10)
        
        # Combobox Tipo de Ayuda
        ctk.CTkLabel(grid_datos, text="Tipo de Ayuda", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.cb_tipo = ctk.CTkComboBox(grid_datos, values=["Cajas de Alimentos", "Materiales Construcción", "Aporte Económico", "Medicamentos", "Gas", "Otros"], width=300, height=35)
        self.cb_tipo.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        # Combobox Producto (Desde Inventario)
        ctk.CTkLabel(grid_datos, text="Producto a Entregar (Inventario)", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w", pady=5)
        self.cb_producto = ctk.CTkComboBox(grid_datos, values=self.cargar_productos_inventario(), width=300, height=35)
        self.cb_producto.grid(row=1, column=1, sticky="ew", pady=(0, 15))
        
        # Cantidad y Valor
        ctk.CTkLabel(grid_datos, text="Cantidad", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_cant = ctk.CTkEntry(grid_datos, placeholder_text="1", height=35)
        self.entry_cant.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        ctk.CTkLabel(grid_datos, text="Valor ($)", font=("Arial", 12, "bold")).grid(row=2, column=1, sticky="w", pady=5)
        self.entry_valor = ctk.CTkEntry(grid_datos, placeholder_text="0", height=35)
        self.entry_valor.grid(row=3, column=1, sticky="ew", pady=(0, 15))

        # Detalle y Quien Retira
        ctk.CTkLabel(form, text="Detalle (Prescrito por Profesional)", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
        self.entry_detalle = ctk.CTkEntry(form, height=35)
        self.entry_detalle.pack(fill="x", padx=30, pady=(5, 15))
        
        ctk.CTkLabel(form, text="Quien Retira (Nombre Completo)", font=("Arial", 12, "bold")).pack(anchor="w", padx=30)
        self.entry_retira = ctk.CTkEntry(form, height=35)
        self.entry_retira.pack(fill="x", padx=30, pady=(5, 25))
        
        # Botón Guardar
        ctk.CTkButton(form, text="💾 Guardar Entrega e Imprimir", height=50, fg_color=COLOR_SIDEBAR, 
                      font=("Arial", 14, "bold"), command=self.guardar_entrega).pack(fill="x", padx=30, side="bottom", pady=30)

        # --- COLUMNA DERECHA: PREVIEW ---
        preview = ctk.CTkFrame(main_grid, fg_color="#ECFDF5", width=300, corner_radius=10)
        preview.pack(side="right", fill="y")
        preview.pack_propagate(False)
        
        ctk.CTkLabel(preview, text="Vista Previa Recibo", font=("Arial", 14, "bold"), text_color="#065F46").pack(pady=30)
        
        ticket = ctk.CTkFrame(preview, fg_color="white", width=220, height=380, corner_radius=0)
        ticket.pack(pady=10)
        
        # Mockup visual del ticket
        ticket_text = """
        RECIBO DE AYUDA
        DIDECO - Municipalidad
        
        Folio: 000XXX
        Fecha: 09-12-2025
        
        --------------------
        Beneficiario:
        (Nombre del Usuario)
        
        RUT: XX.XXX.XXX-X
        --------------------
        
        Detalle:
        Ayuda Social
        
        
        __________________
        Firma Quien Retira
        """
        ctk.CTkLabel(ticket, text=ticket_text, font=("Courier", 10), justify="center", text_color="black").place(relx=0.5, rely=0.5, anchor="center")

    def cargar_productos_inventario(self):
        try:
            # Trae productos con stock positivo
            data = self.db.fetch("SELECT codigo, descripcion, stock FROM inventario WHERE stock > 0")
            if not data: return ["Sin Stock Disponible"]
            return [f"{d[1]} (Stock: {d[2]})" for d in data] # Ej: "Caja Alimentos (Stock: 50)"
        except: return []

    def buscar_beneficiario(self):
        rut = self.entry_rut.get()
        res = self.db.fetch("SELECT nombres, ap_paterno, ap_materno, direccion FROM beneficiarios WHERE rut=?", (rut,))
        
        if res:
            nombre = f"{res[0][0]} {res[0][1]} {res[0][2]}"
            direccion = res[0][3]
            self.lbl_nombre.configure(text=f"Nombre: {nombre}", text_color=COLOR_SIDEBAR)
            self.lbl_direccion.configure(text=f"Dirección: {direccion}")
        else:
            messagebox.showwarning("No encontrado", "El RUT no está registrado en Beneficiarios.")
            self.lbl_nombre.configure(text="Nombre: -", text_color="gray")
            self.lbl_direccion.configure(text="Dirección: -")

    def guardar_entrega(self):
        # Validaciones
        if "Nombre: -" in self.lbl_nombre.cget("text"):
            return messagebox.showerror("Error", "Debe buscar y seleccionar un beneficiario válido.")
        
        if not self.entry_cant.get().isdigit():
            return messagebox.showerror("Error", "La cantidad debe ser un número.")

        # Preparar Datos
        folio = str(self.db.get_folio()).zfill(6)
        rut_ben = self.entry_rut.get()
        nombre_ben = self.lbl_nombre.cget("text").replace("Nombre: ", "")
        
        # Limpiar el nombre del producto para guardar solo el nombre limpio sin el "(Stock: X)"
        prod_full = self.cb_producto.get()
        prod_clean = prod_full.split(" (Stock")[0]
        
        datos = {
            'folio': folio,
            'fecha': date.today().strftime("%d-%m-%Y"),
            'rut': rut_ben,
            'nombres': nombre_ben,
            'tipo': self.cb_tipo.get(),
            'producto': prod_clean,
            'cant': self.entry_cant.get(),
            'valor': self.entry_valor.get(),
            'detalle': self.entry_detalle.get(),
            'retira': self.entry_retira.get()
        }
        
        # 1. Guardar en SQL Entregas
        sql_entrega = """INSERT INTO entregas (rut_beneficiario, fecha, tipo_ayuda, producto, cantidad, valor, detalle, quien_retira) 
                         VALUES (?,?,?,?,?,?,?,?)"""
        
        if self.db.execute(sql_entrega, (datos['rut'], datos['fecha'], datos['tipo'], datos['producto'], 
                                         datos['cant'], datos['valor'], datos['detalle'], datos['retira'])):
            
            # 2. Descontar Stock del Inventario (Lógica simple)
            try:
                cant = int(datos['cant'])
                self.db.execute("UPDATE inventario SET stock = stock - ? WHERE descripcion = ?", (cant, prod_clean))
            except: pass
            
            # 3. Generar PDF
            generar_ticket(datos)
            
            messagebox.showinfo("Éxito", f"Entrega registrada correctamente.\nFolio: {folio}")
            
            # Limpiar campos
            self.entry_rut.delete(0, 'end')
            self.lbl_nombre.configure(text="Nombre: -")
        else:
            messagebox.showerror("Error", "No se pudo guardar la entrega en la base de datos.")