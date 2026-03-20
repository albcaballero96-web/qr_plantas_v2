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

        # -------------------------------
        # 📦 RECUADRO INTERNO
        # -------------------------------
        box_width = 4 * cm
        box_height = 6.3 * cm

        x_box = (page_width - box_width) / 2
        y_box = (page_height - box_height) / 2

        # Dibujar recuadro
        c.rect(x_box, y_box, box_width, box_height)

        # -------------------------------
        # 🔠 TEXTOS SUPERIORES (2 líneas)
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
            page_width/2 - img_width/2,
            y_box + (box_height - img_height)/2 - 0.2*cm,
            img_width,
            img_height
        )

        # -------------------------------
        # 🔻 TEXTO INFERIOR
        # -------------------------------
        planta_txt = str(planta).zfill(3)

        c.drawCentredString(
            page_width / 2,
            y_box + 0.5 * cm,
            f"BLOQUE: {bloque} | N° PLANTA: {planta_txt}"
        )

        c.showPage()

    c.save()

    return temp_pdf.name
