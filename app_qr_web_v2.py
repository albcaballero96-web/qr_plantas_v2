import streamlit as st
import pandas as pd
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import io
import tempfile

# Tamaño de la etiqueta (ANCHO x ALTO)
page_width = 5 * cm
page_height = 7.5 * cm


# -------------------------------
# 🔢 FUNCIÓN PARA GENERAR CÓDIGO
# -------------------------------
def generar_codigo(campana, lote, sublote, bloque, planta, zona):

    lote = str(lote).zfill(5)
    bloque = str(bloque).zfill(2)
    planta = str(planta).zfill(3)

    return f"{campana}{lote}{sublote}{bloque}{planta}{zona}"


# -------------------------------
# 📄 GENERAR PDF
# -------------------------------
def generar_pdf(df):

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    c = canvas.Canvas(temp_pdf.name, pagesize=(page_width, page_height))

    for _, row in df.iterrows():

        campana = str(row["CAMPAÑA"]).strip()
        lote = str(row["LOTE"]).strip()
        sublote = str(row["SUB_LOTE"]).strip()
        bloque = row["BLOQUE"]
        zona = str(row["ZONA"]).strip()
        planta = row["PLANTA"]

        codigo = generar_codigo(
            campana,
            lote,
            sublote,
            bloque,
            planta,
            zona
        )

        # Generar QR
        qr = qrcode.make(codigo)

        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        img = Image.open(buffer)

        # -------------------------------
        # 📦 RECUADRO INTERNO
        # -------------------------------
        box_width = 4 * cm
        box_height = 6.3 * cm

        x_box = (page_width - box_width) / 2
        y_box = (page_height - box_height) / 2

        c.setLineWidth(0.7)
        c.rect(x_box, y_box, box_width, box_height)

        # -------------------------------
        # 🔠 TEXTOS SUPERIORES
        # -------------------------------
        c.setFont("Helvetica-Bold", 8)

        c.drawCentredString(
            page_width / 2,
            y_box + box_height - 0.6 * cm,
            f"{campana} | LOTE: {lote}"
        )
        
        c.drawCentredString(
            page_width / 2,
            y_box + box_height - 1.1 * cm,
            f"SUB-LOTE: {sublote}"
        )

        # -------------------------------
        # 🔲 QR
        # -------------------------------
        img_width = 3.6 * cm
        img_height = 3.6 * cm

        c.drawInlineImage(
            img,
            page_width / 2 - img_width / 2,
            y_box + (box_height - img_height) / 2 - 0.2 * cm,
            img_width,
            img_height
        )

        # -------------------------------
        # 🔻 TEXTO INFERIOR
        # -------------------------------
        c.setFont("Helvetica-Bold", 7)
        
        planta_txt = str(planta).zfill(3)
        
        c.drawCentredString(
            page_width / 2,
            y_box + 0.5 * cm,
            f"BLOQUE: {bloque} | N° PLANTA: {planta_txt}"
        )

        c.showPage()

    c.save()

    return temp_pdf.name


# -------------------------------
# 🌐 INTERFAZ STREAMLIT
# -------------------------------
st.title("Generador de QR para Plantas")

archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)

    # Limpiar nombres de columnas (evita errores)
    df.columns = df.columns.str.strip().str.upper()

    # Validar columnas necesarias
    columnas_necesarias = ["CAMPAÑA", "LOTE", "SUB_LOTE", "BLOQUE", "ZONA", "PLANTA"]

    faltantes = [col for col in columnas_necesarias if col not in df.columns]

    if faltantes:
        st.error(f"Faltan columnas en el Excel: {faltantes}")
        st.stop()

    st.write("Vista previa de los datos")
    st.dataframe(df)

    if st.button("Generar QR"):

        pdf = generar_pdf(df)

        with open(pdf, "rb") as f:

            st.download_button(
                "Descargar PDF",
                f,
                file_name="QR_PLANTAS.pdf",
                mime="application/pdf"
            )
