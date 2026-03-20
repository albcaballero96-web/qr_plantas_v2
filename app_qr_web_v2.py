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
        # 🔵 CÍRCULO DE PERFORACIÓN
        # -------------------------------
        radio = 0.25 * cm  # diámetro = 0.5 cm

        c.circle(
            page_width / 2,
            y_box + box_height - radio - 0.2 * cm,
            radio
        )

        # -------------------------------
        # 🔠 CONTENIDO (AJUSTADO HACIA ABAJO)
        # -------------------------------
        top_margin = 1.5 * cm
        y_top = y_box + box_height - top_margin

        # Texto superior
        c.setFont("Helvetica-Bold", 8)

        c.drawCentredString(
            page_width / 2,
            y_top,
            f"{campana} | LOTE: {lote}"
        )

        c.drawCentredString(
            page_width / 2,
            y_top - 0.45 * cm,
            f"SUB-LOTE: {sublote}"
        )

        # -------------------------------
        # 🔲 QR
        # -------------------------------
        img_width = 3.6 * cm
        img_height = 3.6 * cm

        qr_y = y_top - 0.45 * cm - img_height - 0.2 * cm

        c.drawInlineImage(
            img,
            page_width / 2 - img_width / 2,
            qr_y,
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
            qr_y - 0.35 * cm,
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

    df.columns = df.columns.str.strip().str.upper()

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
