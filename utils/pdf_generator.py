from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
import os

def generar_ticket(datos):
    filename = f"Ticket_{datos['folio']}.pdf"
    c = canvas.Canvas(filename, pagesize=A6)
    w, h = A6
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, h-30, "RECIBO DE AYUDA")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h-45, "DIDECO - Municipalidad")
    c.line(10, h-60, w-10, h-60)
    
    # Body
    text = c.beginText(15, h-80)
    text.setFont("Helvetica", 9)
    text.setLeading(14)
    lines = [
        f"Folio: {datos['folio']}",
        f"Fecha: {datos['fecha']}",
        "-"*35,
        f"Beneficiario: {datos['nombres']}",
        f"RUT: {datos['rut']}",
        "-"*35,
        f"Ayuda: {datos['tipo']}",
        f"Cant: {datos['cant']} | Valor: ${datos['valor']}",
        "-"*35,
        "Detalle:",
        f"{datos['detalle'][:40]}"
    ]
    for l in lines: text.textLine(l)
    c.drawText(text)
    
    # Footer
    c.line(20, 40, w-20, 40)
    c.setFont("Helvetica", 8)
    c.drawCentredString(w/2, 25, "Firma Quien Retira")
    c.drawCentredString(w/2, 15, datos['retira'])
    
    c.save()
    os.startfile(filename)