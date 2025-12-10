import sqlite3
import pyodbc
import os

# Rutas Absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dideco_system.db")

class Database:
    def __init__(self, db_name=DB_PATH):
        self.db_path = db_name
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        # --- TABLAS DEL SISTEMA ---
        
        # 1. CATEGORÍAS Y BENEFICIOS (Se llenarán manualmente o por carga, no semilla)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categorias_ayuda (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tipos_beneficio (
            id INTEGER PRIMARY KEY AUTOINCREMENT, id_categoria INTEGER, nombre TEXT,
            FOREIGN KEY(id_categoria) REFERENCES categorias_ayuda(id)
        )''')

        # 2. INVENTARIO
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE, anio INTEGER, proceso TEXT, obs_linea TEXT,
            direccion TEXT, departamento TEXT, seccion TEXT, precio_compra INTEGER,
            oc_interna TEXT, oc_mercado_publico TEXT, fecha_subida TEXT, 
            cantidad_comprada INTEGER, stock INTEGER
        )''')

        # 3. PROFESIONALES
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS profesionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT UNIQUE, nombres TEXT, apellidos TEXT, cargo TEXT,
            estado TEXT DEFAULT 'Activo', email TEXT
        )''')

        # 4. USUARIOS Y PERMISOS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT UNIQUE, nombres TEXT, apellidos TEXT, cargo TEXT,
            estado TEXT DEFAULT 'Activo', usuario TEXT UNIQUE, contrasena TEXT
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS permisos_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER, modulo TEXT,
            p_nuevo INTEGER DEFAULT 0, p_actualizar INTEGER DEFAULT 0,
            p_eliminar INTEGER DEFAULT 0, p_leer INTEGER DEFAULT 0,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
        )''')

        # 5. BENEFICIARIOS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS beneficiarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT UNIQUE, nombres TEXT, ap_paterno TEXT, ap_materno TEXT,
            direccion TEXT, telefono TEXT, email TEXT
        )''')

        # 6. HISTORIAL DE ENTREGAS
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS entregas (
            folio INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT, rut_beneficiario TEXT, 
            tipo_ayuda TEXT, producto TEXT,
            cantidad INTEGER, valor INTEGER, detalle TEXT,
            quien_retira TEXT, rut_retira TEXT
        )''')

        # --- CARGA ÚNICA DE ADMIN ---
        self.cursor.execute("SELECT count(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            self.crear_admin_por_defecto()

        self.conn.commit()

    def crear_admin_por_defecto(self):
        try:
            # Usuario Admin / 1234
            self.cursor.execute("INSERT INTO usuarios (rut, nombres, apellidos, usuario, contrasena, cargo) VALUES (?,?,?,?,?,?)",
                                ("1-9", "Super", "Admin", "admin", "1234", "Jefe Informática"))
            uid = self.cursor.lastrowid
            
            # Permisos totales
            modulos = ["Inventario", "Profesionales", "Beneficiarios", "Ayudas"]
            for m in modulos:
                self.cursor.execute("INSERT INTO permisos_detalle (id_usuario, modulo, p_nuevo, p_actualizar, p_eliminar, p_leer) VALUES (?,?,?,?,?,?)",
                                    (uid, m, 1, 1, 1, 1))
            print("Usuario Admin creado correctamente.")
        except Exception as e:
            print(f"Error creando admin: {e}")

    # --- MÉTODOS CRUD GENÉRICOS ---
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

    # --- SINCRONIZACIÓN SQL SERVER ---
    def sincronizar_con_sqlserver(self):
        server = '192.168.2.12' 
        database = 'Adquisiciones'            
        username = 'dideco'  
        password = 'App_Dideco_25'             

        try:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            cnxn = pyodbc.connect(conn_str)
            cursor_sql = cnxn.cursor()
            
            query = """
            SELECT
                DS.[Codigo_Producto], DS.[Ano_Proceso], DS.[Obs_Linea],
                DS.[Codigo_Direccion], DS.[Codigo_Departamento], DS.[Codigo_Seccion],
                DS.[Precio_Compra], DS.[Numero_Orden_Compra], DS.[Cantidad],
                OCS.[Numero_Orden_Compra_Chile_Compras], OCS.[Fecha_Subida]
            FROM [Adquisiciones].[dbo].[Detalle_Salida] AS DS
            INNER JOIN [Adquisiciones].[dbo].[Ordenes_Compras_Subidas_Spoke] AS OCS 
                ON DS.[Numero_Orden_Compra] = OCS.[Numero_Orden_Compra];
            """
            
            cursor_sql.execute(query)
            rows = cursor_sql.fetchall()
            
            contador = 0
            for row in rows:
                vals = (
                    row[0], row[1], "Importado", row[2], row[3], row[4], row[5],
                    int(row[6] or 0), row[7], row[9], str(row[10]),
                    int(row[8] or 0), int(row[8] or 0)
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
            return True, f"¡Sincronización Exitosa!\nRegistros: {contador}"
        except Exception as e:
            return False, f"Error SQL Server:\n{e}"