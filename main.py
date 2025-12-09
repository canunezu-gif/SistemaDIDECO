import customtkinter as ctk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageEnhance, ImageDraw
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import threading

from config import *
from database import Database

# Módulos
from modules.dashboard import DashboardView
from modules.inventario import InventarioView
from modules.profesionales import ProfesionalesView
from modules.usuarios import UsuariosView
from modules.beneficiarios import BeneficiariosView
from modules.ayudas import AyudasView
from modules.reportes import ReportesView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Configuración Email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "informatica@munisanpedro.cl"
EMAIL_PASSWORD = "yywg jhdy pkvp ytus" 

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.title("Sistema DIDECO - Gestión Social")
        self.geometry("1366x768")
        self.minsize(1024, 768)
        self.current_view = None
        self.password_visible = False 
        self.mostrar_login()

    def redondear_imagen(self, pil_img, radio=30):
        pil_img = pil_img.convert("RGBA")
        mascara = Image.new('L', pil_img.size, 0)
        draw = ImageDraw.Draw(mascara)
        draw.rounded_rectangle([(0, 0), pil_img.size], radius=radio, fill=255)
        output = Image.new('RGBA', pil_img.size, (0, 0, 0, 0))
        output.paste(pil_img, (0, 0), mask=mascara)
        return output

    def procesar_imagen_fondo(self):
        image_path = os.path.join(ASSETS_DIR, "fondo_login.jpg")
        if not os.path.exists(image_path):
             image_path = os.path.join(ASSETS_DIR, "fondo_login.png")
             if not os.path.exists(image_path): return None
        try:
            img = Image.open(image_path).convert("RGBA")
            img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
            overlay = Image.new('RGBA', img.size, "#0F172A")
            img = Image.blend(img, overlay, 0.90) 
            return ctk.CTkImage(light_image=img, dark_image=img, size=(1920, 1080))
        except: return None

    def cargar_logo_municipal(self):
        logo_path = os.path.join(ASSETS_DIR, "image_1.png")
        if not os.path.exists(logo_path): return None
        try:
            pil_img = Image.open(logo_path)
            base_h = 90
            w_percent = (base_h / float(pil_img.size[1]))
            w_size = int((float(pil_img.size[0]) * float(w_percent)))
            pil_img = pil_img.resize((w_size, base_h), Image.Resampling.LANCZOS)
            pil_img = self.redondear_imagen(pil_img, radio=15)
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w_size, base_h))
        except: return None

    def mostrar_login(self):
        for w in self.winfo_children(): w.destroy()
        bg_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=0)
        bg_frame.pack(fill="both", expand=True)
        bg = self.procesar_imagen_fondo()
        if bg: ctk.CTkLabel(bg_frame, text="", image=bg).place(x=0, y=0, relwidth=1, relheight=1)

        card = ctk.CTkFrame(bg_frame, width=420, height=550, fg_color="#020617", corner_radius=15, border_width=1, border_color="#1E293B")
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False) 
        
        logo_img = self.cargar_logo_municipal()
        if logo_img: ctk.CTkLabel(card, text="", image=logo_img).pack(pady=(40, 10))
        else: ctk.CTkLabel(card, text="MUNICIPIO", font=("Arial", 24, "bold"), text_color="white").pack(pady=(40,10))
        
        ctk.CTkLabel(card, text="Sistema DIDECO", font=("Roboto", 24, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(card, text="Gestor de Ayudas Sociales", font=("Roboto", 13), text_color="#64748B").pack(pady=(0, 30))
        
        ctk.CTkLabel(card, text="Usuario", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(anchor="w", padx=65, pady=(0,5))
        self.u = ctk.CTkEntry(card, placeholder_text="Usuario", width=300, height=45, fg_color="#0F172A", border_color="#334155", text_color="white")
        self.u.pack(pady=(0, 15))
        
        ctk.CTkLabel(card, text="Contraseña", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(anchor="w", padx=65, pady=(0,5))
        pf = ctk.CTkFrame(card, fg_color="transparent", width=300, height=45)
        pf.pack(pady=(0, 10)) 
        self.p = ctk.CTkEntry(pf, placeholder_text="••••••", show="*", width=300, height=45, fg_color="#0F172A", border_color="#334155", text_color="white")
        self.p.place(x=0, y=0)
        self.btn_eye = ctk.CTkButton(pf, text="👁", width=40, height=35, fg_color="transparent", hover_color="#1E293B", text_color="#94A3B8", command=self.toggle_password)
        self.btn_eye.place(x=255, y=5)
        
        lbl_olv = ctk.CTkLabel(card, text="¿Olvidaste la contraseña?", font=("Arial", 11), text_color="#3B82F6", cursor="hand2")
        lbl_olv.pack(pady=(0, 20))
        lbl_olv.bind("<Button-1>", lambda e: self.recuperar_password())
        
        ctk.CTkButton(card, text="Iniciar Sesión", width=300, height=45, fg_color="#2563EB", hover_color="#1D4ED8", font=("Arial", 14, "bold"), command=self.login).pack(pady=(0, 20))
        ctk.CTkLabel(card, text="Municipalidad de San Pedro © 2025", font=("Arial", 10), text_color="#475569").pack(side="bottom", pady=20)

    def toggle_password(self):
        if self.password_visible:
            self.p.configure(show="*"); self.btn_eye.configure(text="👁"); self.password_visible = False
        else:
            self.p.configure(show=""); self.btn_eye.configure(text="Ø"); self.password_visible = True

    def login(self):
        if self.db.fetch("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (self.u.get(), self.p.get())):
            self.setup_main()
        else: messagebox.showerror("Error", "Credenciales incorrectas")

    def recuperar_password(self):
        usuario = ctk.CTkInputDialog(text="Ingrese su USUARIO:", title="Recuperar").get_input()
        if not usuario: return
        if not self.db.fetch("SELECT rut FROM usuarios WHERE usuario=?", (usuario,)):
            return messagebox.showerror("Error", "Usuario no encontrado")
        
        nueva = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
        self.db.execute("UPDATE usuarios SET contrasena=? WHERE usuario=?", (nueva, usuario))
        threading.Thread(target=self.enviar_correo, args=(usuario, nueva)).start()
        messagebox.showinfo("Enviando", "Se están enviando las instrucciones al correo.")

    def enviar_correo(self, usuario, nueva):
        try:
            msg = MIMEMultipart(); msg['From'] = EMAIL_SENDER; msg['To'] = EMAIL_SENDER; msg['Subject'] = "Recuperación Clave DIDECO"
            msg.attach(MIMEText(f"Usuario: {usuario}\nNueva Clave Temporal: {nueva}\n\nCambie su clave al ingresar.", 'plain'))
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT); server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD); server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string()); server.quit()
        except Exception as e: print(e)

    def setup_main(self):
        for w in self.winfo_children(): w.destroy()
        ctk.set_appearance_mode("Light")
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=COLOR_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew"); self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="DIDECO", font=("Arial", 26, "bold"), text_color="white").pack(pady=(40,10))
        ctk.CTkLabel(self.sidebar, text="Gestión Social", text_color="#94A3B8").pack(pady=(0,30))
        
        self.menu_btn("📊 Dashboard", DashboardView)
        self.menu_btn("📦 Inventario", InventarioView)
        self.menu_btn("👔 Profesionales", ProfesionalesView)
        self.menu_btn("👥 Usuarios Sistema", UsuariosView)
        self.menu_btn("🧑‍🤝‍🧑 Beneficiarios", BeneficiariosView)
        self.menu_btn("🤝 Gestión Ayudas", AyudasView)
        self.menu_btn("📄 Reportes", ReportesView)
        
        ctk.CTkButton(self.sidebar, text="Cerrar Sesión", fg_color=COLOR_DANGER, hover_color="#B91C1C", command=self.cerrar_sesion).pack(side="bottom", fill="x", padx=20, pady=30)
        
        # --- SOLUCIÓN: Pegar al techo ---
        self.content_area = ctk.CTkFrame(self, fg_color=COLOR_BG_CONTENT, corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.cambiar_vista(DashboardView)

    def cerrar_sesion(self):
        ctk.set_appearance_mode("Dark"); self.mostrar_login()

    def menu_btn(self, txt, view):
        ctk.CTkButton(self.sidebar, text=txt, fg_color="transparent", anchor="w", hover_color="#1E293B", height=45, command=lambda: self.cambiar_vista(view)).pack(fill="x", padx=10)

    def cambiar_vista(self, view_class):
        if self.current_view: self.current_view.destroy()
        self.current_view = view_class(self.content_area, self.db)
        # --- AQUÍ ESTÁ EL TRUCO: anchor="n" ---
        self.current_view.pack(fill="both", expand=True, anchor="n")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()