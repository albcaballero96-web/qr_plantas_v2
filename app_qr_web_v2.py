import streamlit as st
import pandas as pd
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import io
import tempfile

page_width = 5 * cm
page_height = 7.5 * cm


def generar_codigo(campana, lote, sublote, bloque, planta, zona):

    lote = str(lote).zfill(5)
    bloque = str(bloque).zfill(2)
    planta = str(planta).zfill(3)

    return f"{campana}{lote}{sublote}{bloque}{planta}{zona}"


def generar_pdf(df):

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    c = canvas.Canvas(temp_pdf.name, pagesize=(page_width, page_height))

    for _, row in df.iterrows():

        campana = str(row["CAMPAÑA"])
        lote = str(row["LOTE"])
        sublote = str(row["SUB_LOTE"])
        bloque = row["BLOQUE"]
        zona = str(row["ZONA"])
        planta = row["PLANTA"]

        codigo = generar_codigo(
            campana,
            lote,
            sublote,
            bloque,
            planta,
            zona
        )

        qr = qrcode.make(codigo)

        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        img = Image.open(buffer)

        img_width = 3.8 * cm
        img_height = 3.8 * cm

        c.setFont("Helvetica-Bold", 8)

        c.drawCentredString(
            page_width/2,
            page_height - 0.5*cm,
            f"{campana} | LOTE: {lote} | SUB-LOTE: {sublote}"
        )

        c.drawInlineImage(
            img,
            (page_width-img_width)/2,
            (page_height-img_height)/2 + 0.1*cm,
            img_width,
            img_height
        )

        planta_txt = str(planta).zfill(3)

        c.drawCentredString(
            page_width/2,
            0.6*cm,
            f"BLOQUE: {bloque} | N° PLANTA: {planta_txt}"
        )

        c.showPage()

    c.save()

    return temp_pdf.name


st.title("Generador de QR para Plantas")

archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)

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
