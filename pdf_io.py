import os
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import cm
from datetime import datetime
from reportlab.lib.colors import red, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth
import config
import ui as ui_services


def extract_first_page_from_pdf(pdf_path, txt_path):
    # It would be great if one could extract the whole invoice but not the copy
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        text += '\n\n'  # Agrega dos saltos de línea al final del texto
        with open(txt_path, 'a') as txt_file:
            txt_file.write(text)


def create_and_print_invoice(ui_context, state):
    # Check if folder exists, if not, create it
    if not os.path.exists(config.output_folder):
        os.makedirs(config.output_folder)

    pdf_name = ui_context.cliente_entry.get() + " " + "PX" + ui_context.boleta_entry.get() + ".pdf"
    # Combine folder and filename
    pdf_path = os.path.join(config.output_folder, pdf_name)
    # Crear un nuevo PDF con el tamaño de página A4

    c = canvas.Canvas(pdf_path, pagesize=A4)

    # Calcular los márgenes para centrar el A6 dentro del A4
    # top_margin = A4[1] - A6[1]  # para alinear con el borde de A4
    left_margin = (A4[0] - A6[0]) / 2  # Margen izquierdo para centrar

    # Configurar la fuente
    c.setFont("Helvetica", 9)

    # Extraer los datos del Treeview e imprimirlos en el PDF
    y = A6[1] + 400

    c.drawRightString(
            left_margin + 280,
            y,
            "PX" + str(ui_context.boleta_entry.get()))
    c.drawString(
            left_margin + 10,
            y,
            "Cliente: " +
            str(ui_context.cliente_entry.get()) +
            " " +
            str(ui_context.numero_entry.get()))

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

    for row in ui_context.factura_treeview.get_children():
        # Obtener los valores de la fila
        values = ui_context.factura_treeview.item(row, 'values')

        # Imprimir los valores en el PDF
        c.drawString(left_margin + 10, y, str(values[2]))       # Producto
        c.drawRightString(left_margin + 190, y, str(values[4]))  # Cantidad
        c.drawRightString(left_margin + 230, y, "{:.2f}".format(
                                                float(values[5])))  # Precio
        c.drawRightString(left_margin + 280, y, "{:.2f}".format(
                                                float(values[6])))  # Total

        # Sumar el valor a la variable suma
        suma += float(values[6])
        suma_total += float(values[6])

        # Mover la posición y hacia abajo para la siguiente fila
        y -= 13

        if y < A6[1] + 70:
            # Imprimir la suma de los valores en el final de la página
            if page_number > 1:
                y -= 7
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de paginas anteriores: {:.2f}".format(
                            suma_total - suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(
                    left_margin + 280,
                    y,
                    "PX" + str(ui_context.boleta_entry.get()))
            c.drawString(
                    left_margin + 10,
                    y, "Cliente: " +
                    str(ui_context.cliente_entry.get()) +
                    " " +
                    str(ui_context.numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " +
                                              date_time_str)
            page_number += 1
            c.drawRightString(left_margin + 280, y, "Página: " +
                                                    str(page_number))

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
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de paginas anteriores: {:.2f}".format(
                            suma_total - suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma)
                )

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(
                    left_margin + 280,
                    y,
                    "PX" + str(ui_context.boleta_entry.get()))
            c.drawString(
                    left_margin + 10,
                    y,
                    "Cliente: " +
                    str(ui_context.cliente_entry.get()) +
                    " " +
                    str(ui_context.numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(
                    left_margin + 10,
                    y,
                    "Fecha y hora: " + date_time_str)
            page_number += 1
            c.drawRightString(
                    left_margin + 280,
                    y,
                    "Página: " + str(page_number))

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

        c.drawRightString(
                left_margin + 280,
                y,
                "Suma de la pagina: {:.2f}".format(suma))

        y -= 13

        c.drawRightString(
                left_margin + 280,
                y,
                "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))

        y -= 13

    else:

        y -= 7

    total = ui_context.total_label.cget("text")  # Obtener el texto del total
    total = total.split(" ")[1]  # Quitar la palabra "Subtotal:"
    c.drawRightString(
            left_margin + 280,
            y,
            "Subtotal: {:.2f}".format(float(total)))  # Imprimir el total

    y -= 13

    saldo = state.acreedor_deudor_var.get()  # Obtener el texto del saldo
    saldo = '0' if saldo == '' else saldo
    if float(saldo) <= 0.01:
        c.drawRightString(
                left_margin + 280,
                y,
                "Debe anterior: {:.2f}".format(float(saldo)))
    else:
        c.drawRightString(
                left_margin + 280,
                y,
                "A favor anterior: {:.2f}".format(float(saldo)))

    pago_ef = state.efectivo_var.get()  # Obtener el texto del pago en efectivo
    pago_ef = float(0) if pago_ef == '' else pago_ef
    if pago_ef != 0:
        cash = "Efectivo: {:.2f}".format(float(pago_ef))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, cash)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(
                left_margin + 10,
                y,
                "Efectivo: {:.2f}".format(float(pago_ef)))

    y -= 13

    pago_ch = state.cheque_var.get()
    pago_ch = '0' if pago_ch == '' else pago_ch
    pago_ch = float(pago_ch)
    if pago_ch != 0:
        check = "Cheque: {:.2f}".format(float(pago_ch))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, check)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(
                left_margin + 10,
                y,
                "Cheque: {:.2f}".format(float(pago_ch)))

    totalisimo = ui_context.totalisimo_label.cget("text")
    totalisimo = totalisimo.split(" ")[1]  # Quitar la palabra "Total:"
    c.drawRightString(
            left_margin + 280,
            y,
            "Total a pagar: {:.2f}".format(float(totalisimo)))

    y -= 13

    pago_d = state.dolar_pag.get()
    pago_d = '0' if pago_d == '' else pago_d
    pago_d = float(pago_d)
    if pago_d != 0:
        dollar = "Dolares: {:.2f}".format(float(pago_d))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, dollar)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)

    saldo_fin = ui_context.saldo_final_label.cget("text")
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
        c.drawRightString(
                left_margin + 280,
                y,
                "SALDO FINAL: {:.2f}".format(float(saldo_fin)))

    c.drawString(
            left_margin + 10,
            y + 39,
            "Cantidad de plantas {:.0f}".format(
                float(ui_services.cantidad_de_plantas(ui_context))))

    # DUPLICADO

    c.showPage()

    c.setFont("Helvetica", 9)

    # Extraer los datos del Treeview e imprimirlos en el PDF
    y = A6[1] + 400

    c.drawRightString(
            left_margin + 280,
            y,
            "PX" + str(ui_context.boleta_entry.get()))
    c.drawString(
            left_margin + 10,
            y,
            "Cliente: " + str(ui_context.cliente_entry.get()) +
            " " + str(ui_context.numero_entry.get()))

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

    for row in ui_context.factura_treeview.get_children():
        # Obtener los valores de la fila
        values = ui_context.factura_treeview.item(row, 'values')

        # Imprimir los valores en el PDF
        c.drawString(left_margin + 10, y, str(values[2]))       # Producto
        c.drawRightString(left_margin + 190, y, str(values[4]))  # Cantidad
        c.drawRightString(
                left_margin + 230,
                y,
                "{:.2f}".format(float(values[5])))  # Precio
        c.drawRightString(
                left_margin + 280,
                y,
                "{:.2f}".format(float(values[6])))  # Total

        # Sumar el valor a la variable suma
        suma += float(values[6])
        suma_total += float(values[6])

        # Mover la posición y hacia abajo para la siguiente fila
        y -= 13

        if y < A6[1] + 70:
            # Imprimir la suma de los valores en el final de la página
            if page_number > 1:
                y -= 7
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de paginas anteriores: {:.2f}".format(
                            suma_total - suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(left_margin + 280, y, "PX" + str(
                ui_context.boleta_entry.get()))
            c.drawString(
                    left_margin + 10,
                    y,
                    "Cliente: " +
                    str(ui_context.cliente_entry.get()) +
                    " " +
                    str(ui_context.numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
            c.drawString(left_margin + 180, y, "DUPLICADO")
            page_number += 1
            c.drawRightString(
                    left_margin + 280,
                    y,
                    "Página: " + str(page_number))

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
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de paginas anteriores: {:.2f}".format(
                            suma_total - suma))
                y -= 13
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Subtotal: {:.2f}".format(suma_total))

            else:
                y -= 7
                c.drawRightString(
                        left_margin + 280,
                        y,
                        "Suma de la pagina: {:.2f}".format(suma))

            c.showPage()
            c.setFont("Helvetica", 9)
            y = A6[1] + 400

            c.drawRightString(
                    left_margin + 280,
                    y,
                    "PX" + str(ui_context.boleta_entry.get()))
            c.drawString(
                    left_margin + 10,
                    y,
                    "Cliente: " + str(ui_context.cliente_entry.get()) +
                    " " + str(ui_context.numero_entry.get()))

            y -= 20

            now = datetime.now()
            date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
            c.drawString(left_margin + 10, y, "Fecha y hora: " + date_time_str)
            page_number += 1
            c.drawRightString(
                    left_margin + 280,
                    y,
                    "Página: " + str(page_number))

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

        c.drawRightString(
                left_margin + 280,
                y,
                "Suma de la pagina: {:.2f}".format(suma))

        y -= 13

        c.drawRightString(
                left_margin + 280,
                y,
                "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))

        y -= 13

    else:

        y -= 7

    total = ui_context.total_label.cget("text")  # Obtener el texto del total
    total = total.split(" ")[1]  # Quitar la palabra "Subtotal:"
    c.drawRightString(
            left_margin + 280,
            y,
            "Subtotal: {:.2f}".format(float(total)))  # Imprimir el total

    y -= 13

    saldo = state.acreedor_deudor_var.get()  # Obtener el texto del saldo
    saldo = '0' if saldo == '' else saldo
    if float(saldo) <= 0.01:
        c.drawRightString(
                left_margin + 280,
                y,
                "Debe anterior: {:.2f}".format(float(saldo)))
    else:
        c.drawRightString(
                left_margin + 280,
                y,
                "A favor anterior: {:.2f}".format(float(saldo)))

    pago_ef = state.efectivo_var.get()  # Obtener el texto del pago en efectivo
    pago_ef = float(0) if pago_ef == '' else pago_ef
    if pago_ef != 0:
        cash = "Efectivo: {:.2f}".format(float(pago_ef))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, cash)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(
                left_margin + 10,
                y,
                "Efectivo: {:.2f}".format(float(pago_ef)))

    y -= 13

    pago_ch = state.cheque_var.get()  # Obtener el texto del pago con cheque
    pago_ch = '0' if pago_ch == '' else pago_ch
    pago_ch = float(pago_ch)
    if pago_ch != 0:
        check = "Cheque: {:.2f}".format(float(pago_ch))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, check)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(
                left_margin + 10,
                y,
                "Cheque: {:.2f}".format(float(pago_ch)))

    totalisimo = ui_context.totalisimo_label.cget("text")
    totalisimo = totalisimo.split(" ")[1]  # Quitar la palabra "Total:"
    c.drawRightString(
            left_margin + 280,
            y,
            "Total a pagar: {:.2f}".format(float(totalisimo)))

    y -= 13

    pago_d = state.dolar_pag.get()
    pago_d = '0' if pago_d == '' else pago_d
    pago_d = float(pago_d)
    if pago_d != 0:
        dollar = "Dolares: {:.2f}".format(float(pago_d))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_margin + 10, y, dollar)
        c.setFont("Helvetica", 9)
    else:
        c.setFont("Helvetica", 9)

    saldo_fin = ui_context.saldo_final_label.cget("text")
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
        c.drawRightString(
                left_margin + 280,
                y,
                "SALDO FINAL: {:.2f}".format(float(saldo_fin)))

    # Finalizar y guardar el PDF
    c.save()
    extract_first_page_from_pdf(pdf_path, 'boletas.txt')

    return pdf_path


def print_pdf(pdf_path):
    # Obtiene la impresora predeterminada
    printer_name = win32print.GetDefaultPrinter()

    # Lanza un proceso para imprimir el PDF
    win32api.ShellExecute(0, "print", pdf_path, '/d:"%s"' % printer_name, ".", 0)
