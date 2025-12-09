import os

# Rutas Absolutas (Para evitar errores de "archivo no encontrado")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DB_PATH = os.path.join(BASE_DIR, "dideco_system.db")


# Colores (Paleta DIDECO)
COLOR_SIDEBAR = "#0F172A"       
COLOR_BG_CONTENT = "#F8FAFC"    
COLOR_ACCENT = "#2563EB"        
COLOR_HOVER = "#1E293B"         
COLOR_DANGER = "#EF4444"        
COLOR_TEXT_DARK = "#1E293B"
COLOR_TEXT_LIGHT = "#94A3B8"
