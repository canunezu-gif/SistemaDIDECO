import customtkinter as ctk
from tkinter import messagebox
from config import *

class UsuariosView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        # Header
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(head, text="Gestor de Usuarios", font=("Arial", 26, "bold"), text_color=COLOR_SIDEBAR).pack(side="left")
        ctk.CTkButton(head, text="+ Nuevo Usuario", fg_color=COLOR_SIDEBAR, width=120, command=self.abrir_modal).pack(side="right")
        
        # Tabla Header
        h_frame = ctk.CTkFrame(self, height=40, fg_color="#E2E8F0")
        h_frame.pack(fill="x", padx=30)
        for c in ["USUARIO", "NOMBRE", "CARGO", "PERMISOS", "ACCIONES"]:
            ctk.CTkLabel(h_frame, text=c, font=("Arial", 11, "bold"), text_color="#475569").pack(side="left", expand=True)
            
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=5)
        
        self.cargar()

    def cargar(self):
        for w in self.scroll.winfo_children(): w.destroy()
        rows = self.db.fetch("SELECT id, usuario, nombres, apellidos, cargo, permisos FROM usuarios")
        
        for r in rows:
            uid, user, nom, ape, cargo, perms = r
            
            card = ctk.CTkFrame(self.scroll, fg_color="white", height=50)
            card.pack(fill="x", pady=2)
            
            ctk.CTkLabel(card, text=user, width=100).pack(side="left", expand=True)
            ctk.CTkLabel(card, text=f"{nom} {ape}", width=150).pack(side="left", expand=True)
            ctk.CTkLabel(card, text=cargo, width=100, text_color=COLOR_ACCENT).pack(side="left", expand=True)
            
            # --- CORRECCIÓN DEL ERROR DE PERMISOS ---
            p_box = ctk.CTkFrame(card, fg_color="transparent")
            p_box.pack(side="left", expand=True)
            
            if perms: # Solo si tiene permisos hacemos el split
                for p in perms.split(","):
                    if p: ctk.CTkLabel(p_box, text=p[:3], fg_color="#DBEAFE", text_color="#1E40AF", corner_radius=5, width=30).pack(side="left", padx=1)
            else:
                ctk.CTkLabel(p_box, text="Sin permisos", text_color="gray", font=("Arial", 10)).pack(side="left")

            ctk.CTkButton(card, text="🗑", width=30, fg_color=COLOR_DANGER, command=lambda x=uid: self.borrar(x)).pack(side="right", padx=20)

    def abrir_modal(self):
        t = ctk.CTkToplevel(self)
        t.title("Usuario")
        t.geometry("600x600")
        f = ctk.CTkFrame(t, fg_color="white"); f.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(f, text="Datos Usuario", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        grid = ctk.CTkFrame(f, fg_color="transparent"); grid.pack(fill="x")
        entries = {}
        campos = [("RUT",0,0), ("Usuario",0,1), ("Nombres",1,0), ("Apellidos",1,1), ("Contraseña",2,0), ("Cargo",2,1)]
        
        for l, r, c in campos:
            ctk.CTkLabel(grid, text=l).grid(row=r*2, column=c, sticky="w", padx=10)
            e = ctk.CTkEntry(grid, width=230); e.grid(row=r*2+1, column=c, padx=10, pady=5)
            entries[l] = e
            
        ctk.CTkLabel(f, text="Permisos", font=("Arial", 14, "bold")).pack(anchor="w", pady=20)
        chk_box = ctk.CTkFrame(f, fg_color="#F8FAFC"); chk_box.pack(fill="x", padx=10)
        
        checks = []
        for p in ["CREAR", "LEER", "ACTUALIZAR", "ELIMINAR"]:
            v = ctk.StringVar()
            ctk.CTkCheckBox(chk_box, text=p, variable=v, onvalue=p, offvalue="").pack(side="left", padx=15, pady=15)
            checks.append(v)
            
        def guardar():
            p_str = ",".join([c.get() for c in checks if c.get()])
            v = [entries[k].get() for k in ["RUT","Nombres","Apellidos","Usuario","Contraseña","Cargo"]] + [p_str]
            if self.db.execute("INSERT INTO usuarios (rut, nombres, apellidos, usuario, contrasena, cargo, permisos) VALUES (?,?,?,?,?,?,?)", tuple(v)):
                t.destroy(); self.cargar()
            else: messagebox.showerror("Error", "Error al guardar")
            
        ctk.CTkButton(f, text="Guardar", command=guardar, fg_color=COLOR_SIDEBAR).pack(pady=20)

    def borrar(self, uid):
        if messagebox.askyesno("Borrar", "¿Eliminar usuario?"):
            self.db.execute("DELETE FROM usuarios WHERE id=?", (uid,)); self.cargar()