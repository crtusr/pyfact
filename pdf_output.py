import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import cm
from reportlab.lib.colors import red, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth

# this uses some global state, needs refactor...


def create_and_print_invoice(state):
    campo_escrito = state.acreedor_deudor_var.get()
    if not campo_escrito or '0.0' in campo_escrito:
        update_client()

    # Check if folder exists, if not, create it
    if not os.path.exists(config.output_folder):
        os.makedirs(config.output_folder)

    pdf_name = cliente_entry.get() + " " + "PX" + boleta_entry.get() + ".pdf"
    # Combine folder and filename
    pdf_path = os.path.join(config.output_folder, pdf_name)

    c = canvas.Canvas(pdf_path, pagesize=A4)

    # Calcular los márgenes para centrar el A6 dentro del A4
    top_margin = A4[1] - A6[1]  # Margen superior para alinear con el borde de A4
    left_margin = (A4[0] - A6[0]) / 2  # Margen izquierdo para centrar

    # Configurar la fuente
    c.setFont("Helvetica", 9)

    # Extraer los datos del Treeview e imprimirlos en el PDF
    y = A6[1] + 400

    c.drawRightString(left_margin + 280, y, "PX" + str(boleta_entry.get()))
    c.drawString(left_margin + 10, y, "Cliente: " + str(cliente_entry.get()) + " " + str(numero_entry.get()))

    y -= 20

    now = datetime.now()
    date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
    c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
    page_number = 1
    c.drawRightString(left_margin + 280, y, "Página: " + str(page_number))

    y -= 20

    c.drawString(left_margin + 10, y, "Descripción")       # Producto
    c.drawRightString(left_margin + 190, y, "Cantidad")  # Precio
    c.drawRightString(left_margin + 230, y, "Precio")  # Total
    c.drawRightString(left_margin + 280, y, "Total")  # Total

    y -= 20

    # Inicializar la variable para la suma de los valores
    suma = 0
    suma_total = 0

    for row in factura_treeview.get_children():
        # Obtener los valores de la fila
        values = factura_treeview.item(row, 'values')

        # Imprimir los valores en el PDF
        c.drawString(left_margin + 10, y, str(values[2]))       # Producto
        c.drawRightString(left_margin + 190, y, str(values[4]))  # Cantidad
        c.drawRightString(left_margin + 230, y, "{:.2f}".format(float(values[5])))  # Precio
        c.drawRightString(left_margin + 280, y, "{:.2f}".format(float(values[6])))  # Total

        # Sumar el valor a la variable suma
        suma += float(values[6])
        suma_total += float(values[6])

        # Mover la posición y hacia abajo para la siguiente fila
        y -= 13

        if y < A6[1] + 70:
            # Imprimir la suma de los valores en el final de la página
            if page_number > 1:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(left_margin + 280, y, "PX" + str(boleta_entry.get()))
            c.drawString(left_margin + 10, y, "Cliente: " + str(cliente_entry.get()) + " " + str(numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
            page_number += 1
            c.drawRightString(left_margin + 280, y, "Página: " + str(page_number))

            y -= 20

            c.drawString(left_margin + 10, y, "Descripción")       # Producto
            c.drawRightString(left_margin + 190, y, "Cantidad")  # Precio
            c.drawRightString(left_margin + 230, y, "Precio")  # Total
            c.drawRightString(left_margin + 280, y, "Total")  # Total

            y -= 20

            # Reiniciar la variable suma para la nueva página
            suma = 0

        elif y < A6[1] + 90 and page_number > 1:

            # Imprimir la suma de los valores en el final de la página
            if page_number > 1:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(left_margin + 280, y, "PX" + str(boleta_entry.get()))
            c.drawString(left_margin + 10, y, "Cliente: " + str(cliente_entry.get()) + " " + str(numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
            page_number += 1
            c.drawRightString(left_margin + 280, y, "Página: " + str(page_number))

            y -= 20

            c.drawString(left_margin + 10, y, "Descripción")       # Producto
            c.drawRightString(left_margin + 190, y, "Cantidad")  # Precio
            c.drawRightString(left_margin + 230, y, "Precio")  # Total
            c.drawRightString(left_margin + 280, y, "Total")  # Total

            y -= 20

            # Reiniciar la variable suma para la nueva página
            suma = 0

    if page_number > 1:

        y -= 7

        c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))

        y -= 13

        c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))

        y -= 13

    else:

        y -= 7

    total = total_label.cget("text")  # Obtener el texto del total
    total = total.split(" ")[1]  # Quitar la palabra "Subtotal:"
    c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(float(total)))  # Imprimir el total

    y -= 13

    saldo = acreedor_deudor_var.get()  # Obtener el texto del saldo
    saldo = '0' if saldo == '' else saldo
    if float(saldo) <= 0.01:
        c.drawRightString(left_margin + 280, y, "Debe anterior: {:.2f}".format(float(saldo)))  # Imprimir el saldo
    else:
        c.drawRightString(left_margin + 280, y, "A favor anterior: {:.2f}".format(float(saldo)))  # Imprimir el saldo

    pago_ef = efectivo_var.get()  # Obtener el texto del pago en efectivo
    pago_ef = float(0) if pago_ef == '' else pago_ef
    if pago_ef != 0:
        cash = "Efectivo: {:.2f}".format(float(pago_ef))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, cash)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 10, y, "Efectivo: {:.2f}".format(float(pago_ef)))  # Imprimir el pago en efectivo

    y -= 13

    pago_ch = cheque_var.get()  # Obtener el texto del pago con cheque
    pago_ch = '0' if pago_ch == '' else pago_ch
    pago_ch = float(pago_ch)
    if pago_ch != 0:
        check = "Cheque: {:.2f}".format(float(pago_ch))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, check)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 10, y, "Cheque: {:.2f}".format(float(pago_ch)))  # Imprimir el pago con cheque

    totalisimo = totalisimo_label.cget("text")  # Obtener el texto del totalisimo
    totalisimo = totalisimo.split(" ")[1]  # Quitar la palabra "Total:"
    c.drawRightString(left_margin + 280, y, "Total a pagar: {:.2f}".format(float(totalisimo)))  # Imprimir el totalisimo

    y -= 13

    pago_d = dolar_pag.get()
    pago_d = '0' if pago_d == '' else pago_d
    pago_d = float(pago_d)
    if pago_d != 0:
        dollar = "Dolares: {:.2f}".format(float(pago_d))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, dollar)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)

    saldo_fin = saldo_final_label.cget("text")  # Obtener el texto del saldo final
    saldo_fin = saldo_fin.split(" ")[2]  # Quitar la palabra "Total:"
    saldo_fin_float = float(saldo_fin)
    if saldo_fin_float != 0:
        if saldo_fin_float <= 0:
            debt = "SALDO FINAL DEUDOR: {:.2f}".format(float(saldo_fin))
        elif saldo_fin_float > 0:
            debt = "SALDO FINAL A FAVOR: {:.2f}".format(float(saldo_fin))
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(left_margin + 280, y, debt)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawRightString(left_margin + 280, y, "SALDO FINAL: {:.2f}".format(float(saldo_fin)))  # Imprimir el saldo final

    c.drawString(left_margin + 10, y + 39, "Cantidad de plantas {:.0f}".format(float(cantidad_de_plantas())))

    # DUPLICADO

    c.showPage()

    c.setFont("Helvetica", 9)

    # Extraer los datos del Treeview e imprimirlos en el PDF
    y = A6[1] + 400

    c.drawRightString(left_margin + 280, y, "PX" + str(boleta_entry.get()))
    c.drawString(left_margin + 10, y, "Cliente: " + str(cliente_entry.get()) + " " + str(numero_entry.get()))

    y -= 20

    now = datetime.now()
    date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
    c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
    c.drawString(left_margin + 180, y, "DUPLICADO")
    page_number = 1
    c.drawRightString(left_margin + 280, y, "Página: " + str(page_number))

    y -= 20

    c.drawString(left_margin + 10, y, "Descripción")       # Producto
    c.drawRightString(left_margin + 190, y, "Cantidad")  # Precio
    c.drawRightString(left_margin + 230, y, "Precio")  # Total
    c.drawRightString(left_margin + 280, y, "Total")  # Total

    y -= 20

    # Inicializar la variable para la suma de los valores
    suma = 0
    suma_total = 0

    for row in factura_treeview.get_children():
        # Obtener los valores de la fila
        values = factura_treeview.item(row, 'values')

        # Imprimir los valores en el PDF
        c.drawString(left_margin + 10, y, str(values[2]))       # Producto
        c.drawRightString(left_margin + 190, y, str(values[4]))  # Cantidad
        c.drawRightString(left_margin + 230, y, "{:.2f}".format(float(values[5])))  # Precio
        c.drawRightString(left_margin + 280, y, "{:.2f}".format(float(values[6])))  # Total

        # Sumar el valor a la variable suma
        suma += float(values[6])
        suma_total += float(values[6])

        # Mover la posición y hacia abajo para la siguiente fila
        y -= 13

        if y < A6[1] + 70:
            # Imprimir la suma de los valores en el final de la página
            if page_number > 1:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(left_margin + 280, y, "PX" + str(boleta_entry.get()))
            c.drawString(left_margin + 10, y, "Cliente: " + str(cliente_entry.get()) + " " + str(numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
            c.drawString(left_margin + 180, y, "DUPLICADO")
            page_number += 1
            c.drawRightString(left_margin + 280, y, "Página: " + str(page_number))

            y -= 20

            c.drawString(left_margin + 10, y, "Descripción")       # Producto
            c.drawRightString(left_margin + 190, y, "Cantidad")  # Precio
            c.drawRightString(left_margin + 230, y, "Precio")  # Total
            c.drawRightString(left_margin + 280, y, "Total")  # Total

            y -= 20

            # Reiniciar la variable suma para la nueva página
            suma = 0

        elif y < A6[1] + 90 and page_number > 1:

            # Imprimir la suma de los valores en el final de la página
            if page_number > 1:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(left_margin + 280, y, "PX" + str(boleta_entry.get()))
            c.drawString(left_margin + 10, y, "Cliente: " + str(cliente_entry.get()) + " " + str(numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
            page_number += 1
            c.drawRightString(left_margin + 280, y, "Página: " + str(page_number))

            y -= 20

            c.drawString(left_margin + 10, y, "Descripción")       # Producto
            c.drawRightString(left_margin + 190, y, "Cantidad")  # Precio
            c.drawRightString(left_margin + 230, y, "Precio")  # Total
            c.drawRightString(left_margin + 280, y, "Total")  # Total

            y -= 20

            # Reiniciar la variable suma para la nueva página
            suma = 0

    if page_number > 1:

        y -= 7

        c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))

        y -= 13

        c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))

        y -= 13

    else:

        y -= 7

    total = total_label.cget("text")  # Obtener el texto del total
    total = total.split(" ")[1]  # Quitar la palabra "Subtotal:"
    c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(float(total)))  # Imprimir el total

    y -= 13

    saldo = acreedor_deudor_var.get()  # Obtener el texto del saldo
    saldo = '0' if saldo == '' else saldo
    if float(saldo) <= 0.01:
        c.drawRightString(left_margin + 280, y, "Debe anterior: {:.2f}".format(float(saldo)))  # Imprimir el saldo
    else:
        c.drawRightString(left_margin + 280, y, "A favor anterior: {:.2f}".format(float(saldo)))  # Imprimir el saldo

    pago_ef = efectivo_var.get()  # Obtener el texto del pago en efectivo
    pago_ef = float(0) if pago_ef == '' else pago_ef
    if pago_ef != 0:
        cash = "Efectivo: {:.2f}".format(float(pago_ef))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, cash)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 10, y, "Efectivo: {:.2f}".format(float(pago_ef)))  # Imprimir el pago en efectivo

    y -= 13

    pago_ch = cheque_var.get()  # Obtener el texto del pago con cheque
    pago_ch = '0' if pago_ch == '' else pago_ch
    pago_ch = float(pago_ch)
    if pago_ch != 0:
        check = "Cheque: {:.2f}".format(float(pago_ch))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, check)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 10, y, "Cheque: {:.2f}".format(float(pago_ch)))  # Imprimir el pago con cheque

    totalisimo = totalisimo_label.cget("text")  # Obtener el texto del totalisimo
    totalisimo = totalisimo.split(" ")[1]  # Quitar la palabra "Total:"
    c.drawRightString(left_margin + 280, y, "Total a pagar: {:.2f}".format(float(totalisimo)))  # Imprimir el totalisimo

    y -= 13

    pago_d = dolar_pag.get()
    pago_d = '0' if pago_d == '' else pago_d
    pago_d = float(pago_d)
    if pago_d != 0:
        dollar = "Dolares: {:.2f}".format(float(pago_d))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, dollar)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)

    saldo_fin = saldo_final_label.cget("text")  # Obtener el texto del saldo final
    saldo_fin = saldo_fin.split(" ")[2]  # Quitar la palabra "Total:"
    saldo_fin_float = float(saldo_fin)
    if saldo_fin_float != 0:
        if saldo_fin_float <= 0:
            debt = "SALDO FINAL DEUDOR: {:.2f}".format(float(saldo_fin))
        elif saldo_fin_float > 0:
            debt = "SALDO FINAL A FAVOR: {:.2f}".format(float(saldo_fin))
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(left_margin + 280, y, debt)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawRightString(left_margin + 280, y, "SALDO FINAL: {:.2f}".format(float(saldo_fin)))  # Imprimir el saldo final

    # Finalizar y guardar el PDF
    c.save()
    actualizar_stock()
    extract_first_page_from_pdf(pdf_path, 'boletas.txt')

    return pdf_path
