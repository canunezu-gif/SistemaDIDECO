import sqlite3
import pyodbc
import os

# Ruta absoluta para asegurar que la base de datos se cree en el lugar correcto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dideco_system.db")

class Database:
    def __init__(self, db_name=DB_PATH):
        self.db_path = db_name
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def get_connection(self):
        """Método vital para tu código antiguo: devuelve una conexión nueva."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        # --- 1. TUS TABLAS DEL SISTEMA ORIGINAL (Para compatibilidad) ---
        
        # HISTORIAL DE LOTES (Tu tabla original para control de cargas)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS historial_lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_lote TEXT, fecha_creacion TEXT,
            usuario_creador TEXT, total_items INTEGER
        )''')

        # DETALLE DEL LOTE (Tu tabla original)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS detalle_lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_lote INTEGER, codigo TEXT, descripcion TEXT,
            cantidad INTEGER, precio REAL,
            FOREIGN KEY(id_lote) REFERENCES historial_lotes(id)
        )''')

        # CATEGORÍAS (Tu estructura relacional original)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categorias_ayuda (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tipos_beneficio (
            id INTEGER PRIMARY KEY AUTOINCREMENT, id_categoria INTEGER, nombre TEXT,
            FOREIGN KEY(id_categoria) REFERENCES categorias_ayuda(id)
        )''')

        # --- 2. TABLAS DEL NUEVO SISTEMA INTEGRADO ---

        # INVENTARIO (Tabla principal unificada)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE, anio INTEGER, proceso TEXT, obs_linea TEXT,
            direccion TEXT, departamento TEXT, seccion TEXT, precio_compra INTEGER,
            oc_interna TEXT, oc_mercado_publico TEXT, fecha_subida TEXT, 
            cantidad_comprada INTEGER, stock INTEGER
        )''')

        # PROFESIONALES
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS profesionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT UNIQUE, nombres TEXT, apellidos TEXT, cargo TEXT,
            estado TEXT DEFAULT 'Activo', email TEXT
        )''')

        # USUARIOS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT UNIQUE, nombres TEXT, apellidos TEXT, cargo TEXT,
            estado TEXT DEFAULT 'Activo', usuario TEXT UNIQUE, contrasena TEXT,
            permisos TEXT
        )''')

        # PERMISOS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS permisos (
            id_usuario INTEGER, modulo TEXT,
            p_nuevo INTEGER DEFAULT 0, p_editar INTEGER DEFAULT 0,
            p_eliminar INTEGER DEFAULT 0, p_leer INTEGER DEFAULT 0,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
        )''')

        # BENEFICIARIOS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS beneficiarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT UNIQUE, nombres TEXT, ap_paterno TEXT, ap_materno TEXT,
            direccion TEXT, telefono TEXT, email TEXT
        )''')

        # HISTORIAL DE AYUDAS / ENTREGAS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS entregas (
            folio INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT, rut_beneficiario TEXT, 
            tipo_ayuda TEXT, producto TEXT,
            cantidad INTEGER, valor INTEGER, detalle TEXT,
            quien_retira TEXT, rut_retira TEXT
        )''')

        # --- CARGA DE DATOS SEMILLA (Si la base está vacía) ---
        self.cursor.execute("SELECT count(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            self.cargar_datos_semilla()

        self.conn.commit()

    def cargar_datos_semilla(self):
        # Admin
        try:
            self.cursor.execute("INSERT INTO usuarios (rut, nombres, apellidos, usuario, contrasena, cargo, permisos) VALUES (?,?,?,?,?,?,?)",
                                ("1-9", "Super", "Admin", "admin", "1234", "Jefe Informática", "CREAR,LEER,ACTUALIZAR,ELIMINAR"))
        except: pass

        # Cata (Tu usuario original)
        try:
            self.cursor.execute("INSERT INTO usuarios (rut, nombres, apellidos, usuario, contrasena, cargo, permisos) VALUES (?,?,?,?,?,?,?)",
                                ("2-7", "Cata", "Usuario", "cata", "123", "Asistente", "LEER"))
        except: pass

        # Beneficios Base
        beneficios = {
            "Aporte Económico": ["Ahorro vivienda", "Agua potable", "Gas", "Pago Servicios", "Exención aseo", "Arriendo", "Otros"],
            "Fúnebres": ["Servicios Fúnebres", "Urna", "Sepultación", "Otros Funerales"],
            "Artículos Personales": ["Pañales/Insumos", "Ajuar", "Sabanillas", "Útiles Aseo", "Vestuario", "Otros artículos"],
            "Pasajes y Traslados": ["Entrega pasajes", "Traslados y Fletes", "Reembolso pasajes", "Otros pasajes"],
            "Salud": ["Medicamentos", "Atención Médica/Odont", "Emergencias Salud", "Otros Salud"],
            "Servicios Básicos": ["Agua Potable", "Gas/Leña", "Otros Servicios"],
            "Otros": ["Navidad", "Especie Municipal"]
        }

        for cat, items in beneficios.items():
            try:
                self.cursor.execute("INSERT OR IGNORE INTO categorias_ayuda (nombre) VALUES (?)", (cat,))
                cat_id = self.cursor.execute("SELECT id FROM categorias_ayuda WHERE nombre=?", (cat,)).fetchone()[0]
                for item in items:
                    self.cursor.execute("INSERT OR IGNORE INTO tipos_beneficio (id_categoria, nombre) VALUES (?,?)", (cat_id, item))
            except: pass

    # --- MÉTODOS CRUD GENÉRICOS (Para los módulos nuevos) ---
    def fetch(self, sql, params=()):
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error SQL Fetch: {e}")
            return []

    def execute(self, sql, params=()):
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error SQL Execute: {e}")
            return False

    def get_folio(self):
        res = self.fetch("SELECT seq FROM sqlite_sequence WHERE name='entregas'")
        return res[0][0] + 1 if res else 1

    # --- SINCRONIZACIÓN SQL SERVER (TU CONSULTA EXACTA) ---
    def sincronizar_con_sqlserver(self):
        server = '192.168.2.12' 
        database = 'Adquisiciones'            
        username = 'dideco'  
        password = 'App_Dideco_25'             

        try:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            cnxn = pyodbc.connect(conn_str)
            cursor_sql = cnxn.cursor()
            
            # TU CONSULTA INNER JOIN EXACTA
            query = """
            SELECT
                DS.[Codigo_Producto], DS.[Ano_Proceso], DS.[Obs_Linea],
                DS.[Codigo_Direccion], DS.[Codigo_Departamento], DS.[Codigo_Seccion],
                DS.[Precio_Compra], DS.[Numero_Orden_Compra], DS.[Cantidad],
                OCS.[Numero_Orden_Compra_Chile_Compras], OCS.[Fecha_Subida]
            FROM
                [Adquisiciones].[dbo].[Detalle_Salida] AS DS
            INNER JOIN
                [Adquisiciones].[dbo].[Ordenes_Compras_Subidas_Spoke] AS OCS 
                ON DS.[Numero_Orden_Compra] = OCS.[Numero_Orden_Compra];
            """
            
            cursor_sql.execute(query)
            rows = cursor_sql.fetchall()
            
            contador = 0
            for row in rows:
                # Mapeo: row[0]=Cod, row[1]=Anio, row[2]=Desc ...
                vals = (
                    row[0],             # codigo
                    row[1],             # anio
                    "Importado",        # proceso
                    row[2],             # obs_linea
                    row[3],             # direccion
                    row[4],             # departamento
                    row[5],             # seccion
                    int(row[6] or 0),   # precio
                    row[7],             # oc_interna
                    row[9],             # oc_mercado
                    str(row[10]),       # fecha
                    int(row[8] or 0),   # cantidad_comprada
                    int(row[8] or 0)    # stock (Asumimos stock inicial = cantidad)
                )

                sql_local = """
                INSERT OR REPLACE INTO inventario (
                    codigo, anio, proceso, obs_linea, direccion, departamento, seccion,
                    precio_compra, oc_interna, oc_mercado_publico, fecha_subida, 
                    cantidad_comprada, stock
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.cursor.execute(sql_local, vals)
                contador += 1
            
            self.conn.commit()
            cnxn.close()
            return True, f"¡Sincronización Exitosa!\nSe actualizaron {contador} registros desde Bodega."

        except Exception as e:
            return False, f"Error al conectar con SQL Server:\n{e}"