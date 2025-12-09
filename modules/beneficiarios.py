import customtkinter as ctk
from tkinter import messagebox
from config import *

class BeneficiariosView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Titulo
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(head, text="Gestor de Personas (Beneficiarios)", font=("Arial", 26, "bold"), text_color=COLOR_SIDEBAR).pack(side="left")
        ctk.CTkButton(head, text="+ Nuevo Beneficiario", fg_color=COLOR_SIDEBAR, command=self.abrir_modal).pack(side="right")
        
        # Buscador RUT
        search_fr = ctk.CTkFrame(self, fg_color="white")
        search_fr.pack(fill="x", padx=30)
        ctk.CTkLabel(search_fr, text="Buscar por RUT:").pack(side="left", padx=20)
        self.s_rut = ctk.CTkEntry(search_fr, width=300, placeholder_text="Ej: 12.345.678-9")
        self.s_rut.pack(side="left", padx=10, pady=15)
        ctk.CTkButton(search_fr, text="🔍", width=50, fg_color=COLOR_SIDEBAR, command=self.cargar).pack(side="left")
        
        # Tabla
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=20)
        self.cargar()

    def cargar(self):
        for w in self.scroll.winfo_children(): w.destroy()
        q = f"%{self.s_rut.get()}%"
        rows = self.db.fetch("SELECT id, rut, nombres, ap_paterno, direccion, telefono FROM beneficiarios WHERE rut LIKE ?", (q,))
        
        # Header local
        h = ctk.CTkFrame(self.scroll, height=30, fg_color="#E2E8F0")
        h.pack(fill="x")
        for t in ["RUT", "NOMBRE COMPLETO", "DIRECCIÓN", "CONTACTO", "ACCIONES"]:
            ctk.CTkLabel(h, text=t, font=("Arial", 10, "bold")).pack(side="left", expand=True)

        for r in rows:
            uid, rut, nom, ape, dire, tel = r
            c = ctk.CTkFrame(self.scroll, fg_color="white", height=50)
            c.pack(fill="x", pady=2)
            
            ctk.CTkLabel(c, text=rut).pack(side="left", expand=True)
            ctk.CTkLabel(c, text=f"{nom} {ape}").pack(side="left", expand=True)
            ctk.CTkLabel(c, text=dire).pack(side="left", expand=True)
            ctk.CTkLabel(c, text=tel).pack(side="left", expand=True)
            ctk.CTkButton(c, text="✏️", width=30, fg_color="orange", command=lambda: messagebox.showinfo("Info","Editar en desarrollo")).pack(side="left", expand=True, padx=2)
            ctk.CTkButton(c, text="🗑", width=30, fg_color=COLOR_DANGER, command=lambda x=uid: self.borrar(x)).pack(side="left", expand=True, padx=2)

    def abrir_modal(self):
        t = ctk.CTkToplevel(self)
        t.geometry("700x500")
        t.title("Ficha Social")
        t.attributes("-topmost", True)
        
        f = ctk.CTkFrame(t, fg_color="white"); f.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(f, text="Ficha Social", font=("Arial", 18, "bold")).pack(anchor="w", pady=10)
        
        grid = ctk.CTkFrame(f, fg_color="transparent"); grid.pack(fill="x")
        
        campos = [("RUT",0,0), ("Nombres",0,1), ("Apellido Paterno",1,0), ("Apellido Materno",1,1), ("Dirección",2,0), ("Teléfono",3,0), ("Email",3,1)]
        entries = {}
        for lbl, r, col in campos:
            ctk.CTkLabel(grid, text=lbl).grid(row=r*2, column=col, sticky="w", padx=10)
            e = ctk.CTkEntry(grid, width=300)
            e.grid(row=r*2+1, column=col, padx=10, pady=5)
            entries[lbl] = e
            
        def save():
            v = [entries[k].get() for k in ["RUT", "Nombres", "Apellido Paterno", "Apellido Materno", "Dirección", "Teléfono", "Email"]]
            # Ajuste a la tabla DB
            if self.db.execute("INSERT INTO beneficiarios (rut, nombres, ap_paterno, ap_materno, direccion, telefono, email) VALUES (?,?,?,?,?,?,?)", tuple(v)):
                t.destroy(); self.cargar()
            else: messagebox.showerror("Error", "RUT Duplicado")
            
        ctk.CTkButton(f, text="Guardar Ficha", fg_color=COLOR_SIDEBAR, height=45, command=save).pack(side="bottom", fill="x", pady=20)

    def borrar(self, uid):
        self.db.execute("DELETE FROM beneficiarios WHERE id=?", (uid,)); self.cargar()