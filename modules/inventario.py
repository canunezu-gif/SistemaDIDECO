import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from config import *

class InventarioView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.filtros = {"oc":"", "anio":"", "depto":"", "stock":"Todos", "codigo":"", "desc":"", "seccion":"", "direccion":"", "proceso":"", "pmin":"", "pmax":""}
        self.configurar_estilo_tabla()
        self.setup_ui()
        self.cargar_datos()

    def configurar_estilo_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", background="#E2E8F0", foreground="#1E293B", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

    def setup_ui(self):
        # Header (Reducido pady)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=30, pady=(10, 5)) # ANTES: pady=20
        
        ctk.CTkLabel(head, text="Mantenedor de Inventario", font=("Arial", 26, "bold"), text_color=COLOR_SIDEBAR).pack(side="left")
        
        btns = ctk.CTkFrame(head, fg_color="transparent")
        btns.pack(side="right")
        self.btn_sync = ctk.CTkButton(btns, text="↻ Sincronizar", fg_color="white", text_color=COLOR_SIDEBAR, border_width=1, width=120, command=self.sincronizar_datos)
        self.btn_sync.pack(side="left", padx=5)
        ctk.CTkButton(btns, text="📊 Excel", fg_color="#10B981", width=80, command=self.exportar_excel).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="+ Nuevo", fg_color=COLOR_SIDEBAR, width=100, command=self.abrir_modal).pack(side="left", padx=5)

        # Barra Filtros (Reducido pady)
        bar = ctk.CTkFrame(self, fg_color="white", height=60, corner_radius=10)
        bar.pack(fill="x", padx=30, pady=(5, 10)) # ANTES: pady=(0, 20)
        
        ctk.CTkLabel(bar, text="Buscar:").pack(side="left", padx=(20, 5))
        self.entry_search = ctk.CTkEntry(bar, placeholder_text="Código o Descripción...", width=300)
        self.entry_search.pack(side="left", padx=5, pady=10)
        self.entry_search.bind("<Return>", lambda e: self.cargar_datos())
        
        ctk.CTkButton(bar, text="🔍", width=40, fg_color=COLOR_SIDEBAR, command=self.cargar_datos).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="X", width=40, fg_color="#94A3B8", command=self.limpiar).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="Filtros Avanzados ▾", fg_color="transparent", text_color="#475569", border_width=1, command=self.modal_filtros).pack(side="right", padx=20)

        # Tabla
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        cols = ("ID", "COD", "DESC", "ANIO", "DEPTO", "OC", "STOCK", "PRECIO")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.column("ID", width=0, stretch=False)
        self.tree.column("COD", width=120, stretch=False, anchor="w")
        self.tree.column("DESC", width=400, stretch=True, anchor="w")
        self.tree.column("ANIO", width=60, stretch=False, anchor="center")
        self.tree.column("DEPTO", width=100, stretch=False, anchor="center")
        self.tree.column("OC", width=120, stretch=False, anchor="w")
        self.tree.column("STOCK", width=70, stretch=False, anchor="center")
        self.tree.column("PRECIO", width=90, stretch=False, anchor="e")
        
        headers = ["ID", "CÓDIGO", "DESCRIPCIÓN", "AÑO", "DEPTO", "OC INTERNA", "STOCK", "PRECIO"]
        for i, col in enumerate(cols): self.tree.heading(col, text=headers[i] if col!="ID" else "")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Eliminar", command=self.borrar)
        self.tree.bind("<Button-3>", self.mostrar_menu)

        self.tree.tag_configure('critico', background='#FEF3C7')
        self.tree.tag_configure('vacio', background='#FEE2E2')

        self.lbl_stats = ctk.CTkLabel(self, text="Total items: 0", font=("Arial", 11), text_color="gray")
        self.lbl_stats.pack(side="bottom", anchor="e", padx=30, pady=5)

    def cargar_datos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        sql = "SELECT id, codigo, obs_linea, anio, departamento, oc_interna, stock, precio_compra FROM inventario WHERE 1=1"
        p = []
        txt = self.entry_search.get()
        if txt:
            sql += " AND (codigo LIKE ? OR obs_linea LIKE ?)"; p.extend([f"%{txt}%", f"%{txt}%"])
        if self.filtros["oc"]: sql += " AND oc_interna LIKE ?"; p.append(f"%{self.filtros['oc']}%")
        if self.filtros["anio"]: sql += " AND anio = ?"; p.append(self.filtros['anio'])
        if self.filtros["depto"]: sql += " AND departamento LIKE ?"; p.append(f"%{self.filtros['depto']}%")
        if self.filtros["stock"] == "Crítico": sql += " AND stock <= 5 AND stock > 0"
        elif self.filtros["stock"] == "Sin Stock": sql += " AND stock = 0"
        rows = self.db.fetch(sql, tuple(p))
        for r in rows:
            uid, c, d, a, dep, oc, stk, pr = r
            tag = 'vacio' if stk == 0 else ('critico' if stk <= 5 else '')
            try: pr_fmt = f"${pr:,.0f}".replace(",", ".")
            except: pr_fmt = str(pr)
            self.tree.insert("", "end", values=(uid, c, d, a, dep, oc, stk, pr_fmt), tags=(tag,))
        self.lbl_stats.configure(text=f"Total: {len(rows)}")

    def sincronizar_datos(self):
        self.btn_sync.configure(state="disabled", text="Conectando...")
        self.update_idletasks()
        exito, msg = self.db.sincronizar_con_sqlserver()
        self.btn_sync.configure(state="normal", text="↻ Sincronizar")
        if exito: messagebox.showinfo("Éxito", msg); self.cargar_datos()
        else: messagebox.showerror("Error", msg)

    def exportar_excel(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if f:
            data = [self.tree.item(i)['values'] for i in self.tree.get_children()]
            df = pd.DataFrame(data, columns=["ID", "COD", "DESC", "ANIO", "DEPTO", "OC", "STOCK", "PRECIO"])
            df.drop("ID", axis=1, inplace=True)
            df.to_excel(f, index=False)
            messagebox.showinfo("Listo", "Excel exportado")

    def modal_filtros(self):
        t = ctk.CTkToplevel(self)
        t.title("Filtros")
        t.geometry("600x500")
        f = ctk.CTkFrame(t, fg_color="white"); f.pack(fill="both", expand=True, padx=20, pady=20)
        campos = [("Año", "anio"), ("Descripción", "desc"), ("Departamento", "depto")]
        ens = {}
        for l, k in campos:
            ctk.CTkLabel(f, text=l).pack(anchor="w")
            e = ctk.CTkEntry(f); e.pack(fill="x"); e.insert(0, self.filtros.get(k,""))
            ens[k] = e
        ctk.CTkLabel(f, text="Stock").pack(anchor="w")
        cb = ctk.CTkComboBox(f, values=["Todos", "Crítico", "Sin Stock"])
        cb.pack(fill="x")
        def apl():
            for k in ens: self.filtros[k] = ens[k].get()
            self.filtros["stock"] = cb.get()
            self.cargar_datos(); t.destroy()
        ctk.CTkButton(f, text="Filtrar", command=apl).pack(pady=20)

    def limpiar(self):
        self.entry_search.delete(0, 'end')
        self.filtros = {k:"" for k in self.filtros}; self.filtros["stock"]="Todos"
        self.cargar_datos()

    def mostrar_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item: self.tree.selection_set(item); self.menu.post(event.x_root, event.y_root)

    def borrar(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Confirmar", "¿Eliminar?"):
            self.db.execute("DELETE FROM inventario WHERE id=?", (self.tree.item(sel[0])['values'][0],))
            self.cargar_datos()

    def abrir_modal(self):
        # Lógica de nuevo producto
        pass