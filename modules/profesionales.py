import customtkinter as ctk
from tkinter import messagebox
from config import *

class ProfesionalesView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # --- Cabecera ---
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(head, text="Gestor de Profesionales", font=("Arial", 26, "bold"), text_color=COLOR_SIDEBAR).pack(side="left")
        ctk.CTkButton(head, text="+ Nuevo Profesional", fg_color=COLOR_SIDEBAR, height=40, command=self.abrir_modal).pack(side="right")
        
        # --- Barra de Filtros ---
        filter_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        filter_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        self.entry_search = ctk.CTkEntry(filter_frame, placeholder_text="Buscar por RUT o Nombre...", width=300, border_color="#E2E8F0")
        self.entry_search.pack(side="left", padx=15, pady=10)
        ctk.CTkButton(filter_frame, text="Buscar", fg_color=COLOR_ACCENT, width=100, command=self.cargar_tabla).pack(side="left", padx=5)
        
        # --- Tabla de Datos ---
        # Encabezados
        header_row = ctk.CTkFrame(self, height=40, fg_color="#F1F5F9")
        header_row.pack(fill="x", padx=30)
        cols = ["RUT", "NOMBRE COMPLETO", "CARGO", "EMAIL", "ESTADO", "ACCIONES"]
        for col in cols:
            ctk.CTkLabel(header_row, text=col, font=("Arial", 11, "bold"), text_color="#64748B").pack(side="left", expand=True)

        # Contenedor Scroll
        self.scroll_table = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_table.pack(fill="both", expand=True, padx=30, pady=5)
        
        self.cargar_tabla()

    def cargar_tabla(self):
        # Limpiar
        for widget in self.scroll_table.winfo_children(): widget.destroy()
        
        busqueda = f"%{self.entry_search.get()}%"
        sql = "SELECT id, rut, nombres, apellidos, cargo, email, estado FROM profesionales WHERE rut LIKE ? OR nombres LIKE ?"
        registros = self.db.fetch(sql, (busqueda, busqueda))
        
        if not registros:
            ctk.CTkLabel(self.scroll_table, text="No se encontraron profesionales.").pack(pady=20)
            return

        for row in registros:
            id_prof, rut, nom, ape, cargo, email, estado = row
            
            card = ctk.CTkFrame(self.scroll_table, fg_color="white", height=50)
            card.pack(fill="x", pady=2)
            
            # Celdas
            ctk.CTkLabel(card, text=rut, width=100).pack(side="left", expand=True)
            ctk.CTkLabel(card, text=f"{nom} {ape}", width=150).pack(side="left", expand=True)
            ctk.CTkLabel(card, text=cargo, width=100).pack(side="left", expand=True)
            ctk.CTkLabel(card, text=email, width=150, text_color="gray").pack(side="left", expand=True)
            
            # Badge de Estado
            color_st = "#DCFCE7" if estado == "Activo" else "#FEE2E2"
            text_st = "#166534" if estado == "Activo" else "#991B1B"
            lbl_st = ctk.CTkLabel(card, text=estado, fg_color=color_st, text_color=text_st, corner_radius=5, width=60)
            lbl_st.pack(side="left", expand=True)
            
            # Botón Eliminar
            btn_del = ctk.CTkButton(card, text="🗑", width=30, fg_color=COLOR_DANGER, hover_color="#B91C1C", 
                                    command=lambda x=id_prof: self.eliminar(x))
            btn_del.pack(side="right", padx=20)

    def abrir_modal(self):
        t = ctk.CTkToplevel(self)
        t.title("Registro de Funcionario")
        t.geometry("600x550")
        t.attributes("-topmost", True)
        t.configure(fg_color="#F8FAFC")
        
        # Formulario
        f = ctk.CTkFrame(t, fg_color="white", corner_radius=10)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(f, text="Nuevo Funcionario", font=("Arial", 18, "bold"), text_color=COLOR_SIDEBAR).pack(anchor="w", pady=20, padx=20)
        
        entries = {}
        campos = [("RUT", "text"), ("Nombres", "text"), ("Apellidos", "text"), ("Cargo", "text"), ("Email", "text")]
        
        for lbl, _ in campos:
            ctk.CTkLabel(f, text=lbl, font=("Arial", 12, "bold"), text_color="#475569").pack(anchor="w", padx=20)
            e = ctk.CTkEntry(f, height=35, border_color="#E2E8F0")
            e.pack(fill="x", padx=20, pady=(0, 10))
            entries[lbl] = e
            
        ctk.CTkLabel(f, text="Estado", font=("Arial", 12, "bold"), text_color="#475569").pack(anchor="w", padx=20)
        cb_estado = ctk.CTkComboBox(f, values=["Activo", "Inactivo"], height=35)
        cb_estado.pack(fill="x", padx=20, pady=(0, 20))
        
        def guardar():
            datos = [entries[c].get() for c in ["RUT", "Nombres", "Apellidos", "Cargo", "Email"]]
            datos.append(cb_estado.get())
            
            if self.db.execute("INSERT INTO profesionales (rut, nombres, apellidos, cargo, email, estado) VALUES (?,?,?,?,?,?)", tuple(datos)):
                messagebox.showinfo("Éxito", "Profesional guardado correctamente.")
                t.destroy()
                self.cargar_tabla()
            else:
                messagebox.showerror("Error", "No se pudo guardar. Verifique si el RUT ya existe.")

        ctk.CTkButton(f, text="Guardar Registro", fg_color=COLOR_SIDEBAR, height=45, command=guardar).pack(fill="x", padx=20, side="bottom", pady=20)

    def eliminar(self, id_prof):
        if messagebox.askyesno("Confirmar", "¿Realmente desea eliminar a este profesional?"):
            self.db.execute("DELETE FROM profesionales WHERE id=?", (id_prof,))
            self.cargar_tabla()