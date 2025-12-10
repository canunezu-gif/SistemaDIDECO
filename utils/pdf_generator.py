from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.lib.colors import black, lightgrey
import os

def generar_ticket(datos):
    """
    Genera un comprobante PDF idéntico al formato físico solicitado.
    """
    filename = f"Comprobante_{datos['folio']}.pdf"
    
    # Tamaño A5 (Media carta aprox, bueno para recibos)
    c = canvas.Canvas(filename, pagesize=A5)
    width, height = A5
    
    # --- 1. ENCABEZADO ---
    # Logo o Nombre Municipalidad
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 1.5*cm, "MUNICIPALIDAD DE SAN PEDRO")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, height - 2.2*cm, "DIRECCIÓN DE DESARROLLO COMUNITARIO (DIDECO)")
    c.drawCentredString(width/2, height - 2.7*cm, "COMPROBANTE DE ENTREGA DE BENEFICIO SOCIAL")
    
    # Cuadro del Folio (Esquina superior derecha)
    c.setLineWidth(1)
    c.rect(width - 5.5*cm, height - 4*cm, 4.5*cm, 1*cm)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 5.2*cm, height - 3.65*cm, f"FOLIO N°: {datos['folio']}")

    # --- 2. DATOS DEL BENEFICIARIO ---
    y_start = height - 5*cm
    
    # Título Sección
    c.setFillColor(lightgrey)
    c.rect(1.5*cm, y_start, width - 3*cm, 0.6*cm, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.7*cm, y_start + 0.15*cm, "I. ANTECEDENTES DEL BENEFICIARIO")
    
    y = y_start - 0.8*cm
    c.setFont("Helvetica", 10)
    
    # Fila 1: Nombre y RUT
    c.drawString(2*cm, y, "NOMBRE:")
    c.drawString(4.5*cm, y, datos['nombres'].upper())
    
    c.drawString(2*cm, y - 0.6*cm, "R.U.T.:")
    c.drawString(4.5*cm, y - 0.6*cm, datos['rut'])
    
    # Fila 2: Dirección
    y -= 1.2*cm
    c.drawString(2*cm, y, "DIRECCIÓN:")
    c.drawString(4.5*cm, y, datos['direccion'].upper())

    # --- 3. DETALLE DEL BENEFICIO ---
    y -= 1.5*cm
    
    # Título Sección
    c.setFillColor(lightgrey)
    c.rect(1.5*cm, y, width - 3*cm, 0.6*cm, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1.7*cm, y + 0.15*cm, "II. DETALLE DE LA AYUDA ENTREGADA")
    
    y -= 0.8*cm
    c.setFont("Helvetica", 10)
    
    # Tabla de datos
    c.drawString(2*cm, y, "FECHA ENTREGA:")
    c.drawString(6*cm, y, datos['fecha'])
    
    y -= 0.6*cm
    c.drawString(2*cm, y, "TIPO BENEFICIO:")
    c.drawString(6*cm, y, datos['tipo'].upper())
    
    y -= 0.6*cm
    c.drawString(2*cm, y, "ITEM / PRODUCTO:")
    c.drawString(6*cm, y, datos['producto'])
    
    y -= 0.6*cm
    c.drawString(2*cm, y, "CANTIDAD:")
    c.drawString(6*cm, y, str(datos['cant']))
    
    y -= 0.6*cm
    c.drawString(2*cm, y, "VALOR REFERENCIAL:")
    c.drawString(6*cm, y, f"$ {datos['valor']}")
    
    y -= 0.6*cm
    c.drawString(2*cm, y, "DETALLE / OBS:")
    c.drawString(6*cm, y, datos['detalle'])

    # --- 4. FIRMA DE RECEPCIÓN ---
    y_firma = 3.5*cm
    
    c.line(width/2 - 4*cm, y_firma, width/2 + 4*cm, y_firma)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width/2, y_firma - 0.5*cm, "RECIBÍ CONFORME")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, y_firma - 1.2*cm, datos['retira'].upper())
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, y_firma - 1.6*cm, f"(Nombre Quien Retira)")
    
    if datos['retira'].upper() != datos['nombres'].upper():
         c.drawCentredString(width/2, y_firma - 2.0*cm, "En representación del beneficiario")

    # Guardar y abrir
    c.save()
    try:
        os.startfile(filename)
    except:
        pass # En sistemas no Windows podría fallar el startfile