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

# Importaciones de configuración y base de datos
from config import *
from database import Database

# Importar Módulos del Sistema
from modules.dashboard import DashboardView
from modules.inventario import InventarioView
from modules.profesionales import ProfesionalesView
from modules.usuarios import UsuariosView
from modules.beneficiarios import BeneficiariosView
from modules.ayudas import AyudasView
from modules.reportes import ReportesView

# Configuración Visual Global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Configuración Correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "informatica@munisanpedro.cl"
EMAIL_PASSWORD = "yywg jhdy pkvp ytus" 

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Intentar conectar a la BD
        try:
            self.db = Database()
        except Exception as e:
            messagebox.showerror("Error Fatal", f"Error al iniciar base de datos:\n{e}")
            self.destroy()
            return

        self.title("Sistema DIDECO - Gestión Social")
        self.geometry("1366x768")
        self.minsize(1024, 768)
        
        self.current_view = None
        self.password_visible = False 
        
        self.mostrar_login()

    # --- UTILIDADES VISUALES ---
    def redondear_imagen(self, pil_img, radio=30):
        """Redondea las esquinas de una imagen para el logo"""
        pil_img = pil_img.convert("RGBA")
        mascara = Image.new('L', pil_img.size, 0)
        draw = ImageDraw.Draw(mascara)
        draw.rounded_rectangle([(0, 0), pil_img.size], radius=radio, fill=255)
        output = Image.new('RGBA', pil_img.size, (0, 0, 0, 0))
        output.paste(pil_img, (0, 0), mask=mascara)
        return output

    def procesar_imagen_fondo(self):
        """Carga el fondo y le aplica el filtro azul oscuro"""
        image_path = os.path.join(ASSETS_DIR, "fondo_login.jpg")
        if not os.path.exists(image_path):
             image_path = os.path.join(ASSETS_DIR, "fondo_login.png")
             if not os.path.exists(image_path): return None

        try:
            img = Image.open(image_path).convert("RGBA")
            img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
            # Filtro azul corporativo sobre la foto
            overlay = Image.new('RGBA', img.size, "#0F172A")
            img = Image.blend(img, overlay, 0.90) 
            return ctk.CTkImage(light_image=img, dark_image=img, size=(1920, 1080))
        except: return None

    def cargar_logo_municipal(self):
        """Carga el logo y lo redondea suavemente"""
        logo_path = os.path.join(ASSETS_DIR, "image_1.png")
        if not os.path.exists(logo_path): return None
        try:
            pil_img = Image.open(logo_path)
            # Redimensionar
            base_h = 100 
            w_percent = (base_h / float(pil_img.size[1]))
            w_size = int((float(pil_img.size[0]) * float(w_percent)))
            pil_img = pil_img.resize((w_size, base_h), Image.Resampling.LANCZOS)
            # Redondear
            pil_img = self.redondear_imagen(pil_img, radio=20)
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w_size, base_h))
        except: return None

    # --- PANTALLA LOGIN ---
    def mostrar_login(self):
        for w in self.winfo_children(): w.destroy()
        
        # Fondo
        bg_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=0)
        bg_frame.pack(fill="both", expand=True)
        self.bg_image = self.procesar_imagen_fondo()
        if self.bg_image:
            ctk.CTkLabel(bg_frame, text="", image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)

        # Tarjeta Login (Tamaño corregido: Más ancha y alta para que respiren los inputs)
        card = ctk.CTkFrame(bg_frame, width=480, height=620, fg_color="#020617", 
                            corner_radius=20, border_width=1, border_color="#1E293B")
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False) # Respetar tamaño fijo
        
        # Logo
        logo_img = self.cargar_logo_municipal()
        if logo_img:
            ctk.CTkLabel(card, text="", image=logo_img).pack(pady=(50, 20))
        else:
            ctk.CTkLabel(card, text="MUNICIPIO", font=("Arial", 24, "bold"), text_color="white").pack(pady=(50,20))
        
        ctk.CTkLabel(card, text="Sistema DIDECO", font=("Roboto", 24, "bold"), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(card, text="Gestor de Ayudas Sociales", font=("Roboto", 13), text_color="#64748B").pack(pady=(0, 40))
        
        # Inputs (Con márgenes laterales correctos)
        ctk.CTkLabel(card, text="Usuario", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(anchor="w", padx=65, pady=(0,5))
        self.u = ctk.CTkEntry(card, placeholder_text="Ingrese su usuario", width=350, height=50, 
                              fg_color="#0F172A", border_color="#334155", text_color="white", corner_radius=10)
        self.u.pack(pady=(0, 25))
        
        ctk.CTkLabel(card, text="Contraseña", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(anchor="w", padx=65, pady=(0,5))
        
        pass_frame = ctk.CTkFrame(card, fg_color="transparent", width=350, height=50)
        pass_frame.pack(pady=(0, 10))
        
        self.p = ctk.CTkEntry(pass_frame, placeholder_text="••••••••", show="*", width=350, height=50, 
                              fg_color="#0F172A", border_color="#334155", text_color="white", corner_radius=10)
        self.p.place(x=0, y=0)
        
        # Botón Ojo
        self.btn_eye = ctk.CTkButton(pass_frame, text="👁", width=40, height=40, fg_color="transparent", 
                                     hover_color="#1E293B", text_color="#94A3B8", font=("Arial", 16),
                                     command=self.toggle_password)
        self.btn_eye.place(x=300, y=5)
        
        # Link Recuperar
        link_pass = ctk.CTkLabel(card, text="¿Olvidaste la contraseña?", font=("Arial", 11), text_color="#3B82F6", cursor="hand2")
        link_pass.pack(pady=(0, 30))
        link_pass.bind("<Button-1>", lambda e: self.recuperar_password())
        
        # Botón Iniciar
        ctk.CTkButton(card, text="Iniciar Sesión", width=350, height=50, 
                      fg_color="#2563EB", hover_color="#1D4ED8", 
                      font=("Arial", 15, "bold"), corner_radius=10,
                      command=self.login).pack(pady=(0, 20))
        
        ctk.CTkLabel(card, text="Municipalidad de San Pedro © 2025", font=("Arial", 10), text_color="#475569").pack(side="bottom", pady=25)

    # --- LÓGICA LOGIN ---
    def toggle_password(self):
        if self.password_visible:
            self.p.configure(show="*"); self.btn_eye.configure(text="👁"); self.password_visible = False
        else:
            self.p.configure(show=""); self.btn_eye.configure(text="Ø"); self.password_visible = True

    def login(self):
        # Admin Bypass
        if self.u.get() == "admin" and self.p.get() == "1234":
            self.setup_main_interface()
            return

        # Verificación BD
        user = self.db.fetch("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (self.u.get(), self.p.get()))
        if user:
            self.setup_main_interface()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")

    def recuperar_password(self):
        usuario = ctk.CTkInputDialog(text="Ingrese su nombre de USUARIO:", title="Recuperar Contraseña").get_input()
        if not usuario: return

        res = self.db.fetch("SELECT rut FROM usuarios WHERE usuario=?", (usuario,))
        if not res:
            messagebox.showerror("Error", "Usuario no encontrado en el sistema.")
            return

        # Generar clave temporal
        chars = string.ascii_letters + string.digits
        nueva_pass = ''.join(random.choice(chars) for i in range(8))
        
        self.db.execute("UPDATE usuarios SET contrasena=? WHERE usuario=?", (nueva_pass, usuario))
        
        # Enviar correo en hilo separado
        threading.Thread(target=self.enviar_correo, args=(usuario, nueva_pass)).start()
        messagebox.showinfo("Procesando", f"Se están enviando las instrucciones de recuperación al correo institucional.")

    def enviar_correo(self, usuario, nueva_pass):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_SENDER # En producción usar email del usuario
            msg['Subject'] = "Recuperación de Contraseña - DIDECO"
            cuerpo = f"Usuario: {usuario}\nNueva Clave Temporal: {nueva_pass}\n\nPor favor cambie su clave al ingresar."
            msg.attach(MIMEText(cuerpo, 'plain'))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Error correo: {e}")

    # --- INTERFAZ PRINCIPAL ---
    def setup_main_interface(self):
        for w in self.winfo_children(): w.destroy()
        ctk.set_appearance_mode("Light") 
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=COLOR_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="DIDECO", font=("Arial", 26, "bold"), text_color="white").pack(pady=(40,5), padx=25, anchor="w")
        ctk.CTkLabel(self.sidebar, text="Gestión Social", font=("Arial", 12), text_color="#64748B").pack(pady=(0,30), padx=25, anchor="w")
        
        # Botones del Menú
        self.add_menu_btn("📊 Dashboard", DashboardView)
        self.add_menu_btn("📦 Inventario", InventarioView)
        self.add_menu_btn("👔 Profesionales", ProfesionalesView)
        self.add_menu_btn("👥 Usuarios Sistema", UsuariosView)
        self.add_menu_btn("🧑‍🤝‍🧑 Beneficiarios", BeneficiariosView)
        self.add_menu_btn("🤝 Gestión Ayudas", AyudasView)
        self.add_menu_btn("📄 Reportes", ReportesView)
        
        ctk.CTkButton(self.sidebar, text="Cerrar Sesión", fg_color=COLOR_DANGER, hover_color="#B91C1C", height=45, 
                      command=self.cerrar_sesion).pack(side="bottom", fill="x", padx=20, pady=30)
        
        # Contenido Principal (CORRECCIÓN ESPACIO EN BLANCO: corner_radius=0)
        self.content_area = ctk.CTkFrame(self, fg_color=COLOR_BG_CONTENT, corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        
        self.cambiar_vista(DashboardView)

    def cerrar_sesion(self):
        ctk.set_appearance_mode("Dark")
        self.mostrar_login()

    def add_menu_btn(self, text, view_class):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color="#E2E8F0", anchor="w", 
                            hover_color="#1E293B", height=45, font=("Arial", 13),
                            command=lambda: self.cambiar_vista(view_class))
        btn.pack(fill="x", padx=10, pady=2)

    def cambiar_vista(self, view_class):
        if self.current_view: self.current_view.destroy()
        self.current_view = view_class(self.content_area, self.db)
        # CORRECCIÓN ESPACIO EN BLANCO: anchor="n" para pegar al techo
        self.current_view.pack(fill="both", expand=True, anchor="n")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()