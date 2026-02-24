import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Grid
from dbfread import DBF
from tkinter.font import Font
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import cm
from datetime import datetime
from reportlab.lib.colors import red, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth
import math
import os
import sys
import pdfplumber

"""para la cotizacion del dolar"""

import requests
from bs4 import BeautifulSoup

window = tk.Tk()

arial_font = Font(family='Arial', size=13)

# Change the font for all Listboxes that are part of a Combobox
window.option_add("*TCombobox*Listbox*Font", arial_font)

window.title("Facturador")

PRECIOB_var = tk.StringVar()
precio_bonificado_var = tk.IntVar()
precio_iva_var = tk.IntVar()
TAMAÑO_var = tk.StringVar()
numero_var = tk.StringVar()
acreedor_var = tk.StringVar()
deudor_var = tk.StringVar()
acreedor_deudor_var = tk.StringVar()
existencias_var = tk.StringVar()
codigo_var = tk.StringVar()
efectivo_var = tk.StringVar()
cheque_var = tk.StringVar()
CUIT_var = tk.StringVar()
numero_fila_var = tk.IntVar()
dolar_var = tk.StringVar(value="0.0")
dolar_pag = tk.StringVar(value="0.0")

def buscar_valor():
    """Busca los valores de compra y venta del dólar blue."""
    #url = "https://dolarhoy.com/cotizaciondolarblue"
    url = "https://dolarhoy.com"

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        compra_div = soup.find("div", class_="val")
        venta_divs = soup.find_all("div", class_="val")

        if compra_div and len(venta_divs) > 1:
            compra = compra_div.text.strip()
            venta = venta_divs[1].text.strip()

            # Limpiar y convertir a números (reemplazar ',' por '.' y eliminar '$')
            compra = float(compra.replace('$', '').replace(',', '.'))
            venta = float(venta.replace('$', '').replace(',', '.'))

            promedio = (compra + venta) / 2

            dolar_var.set(promedio)

            saldot = calcular_total() / promedio
            
            
            messagebox.showinfo("Resultado", f"Compra: {compra}\nVenta: {venta}\nPromedio: {promedio}\n\n A pagar: {saldot}")
        else:
            messagebox.showinfo("Resultado", "No se pudieron obtener los valores de compra y venta.")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error al acceder a la URL: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Error al convertir valores a números: {e}")  #Maneja errores de conversión
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")



def extract_first_page_from_pdf(pdf_path, txt_path):
   with pdfplumber.open(pdf_path) as pdf:
       first_page = pdf.pages[0]
       text = first_page.extract_text()
       text += '\n\n' # Agrega dos saltos de línea al final del texto
       with open(txt_path, 'a') as txt_file:
           txt_file.write(text)

def reset_program():
    producto_entry.delete(0, 'end')
    cliente_entry.delete(0, 'end')
    cantidad_entry.delete(0, 'end')
    precio_entry.delete(0, tk.END)
    existencia_entry.delete(0, tk.END)
    producto_entry.delete(0, tk.END)
    cantidad_entry.delete(0, tk.END)
    tamaño_entry.delete(0, tk.END)
    cliente_entry.delete(0, tk.END)
    boleta_entry.delete(0, tk.END)
    codi_entry.delete(0, tk.END)
    acreedor_deudor_entry.delete(0, tk.END)
    efectivo_entry.delete(0, tk.END)
    cheque_entry.delete(0, tk.END)
    numero_entry.delete(0, tk.END)
    cuit_entry.delete(0, tk.END)
    dolares_entry.delete(0, tk.END)
    numero_fila_var.set(0)
    cliente_entry.focus_set()

    # Clear the Treeview
    for item in factura_treeview.get_children():
        factura_treeview.delete(item)

    calcular_total()

reset_button = tk.Button(window, text="Nueva boleta", command=reset_program)
reset_button.grid(row=0, column=5)

def update_price(*args):
    if var.get():
        # Aumenta el precio en un 30% y redondea hacia arriba a las decenas más cercanas
        new_price = math.ceil((float(precio_entry.get()) * 1.3) / 10.0) * 10
        precio_entry.delete(0, tk.END)
        print(str(new_price))
        precio_entry.insert(0, str(new_price))

def autocomplete(event=None):
    current_text = producto_entry.get().lower()
    suggestions = [row for row in stock if current_text in row['NOMBRE'].lower()]
    if suggestions:
        suggestions_sorted = sorted(suggestions, key=lambda row: row['NOMBRE'])

        suggestions_with_size_and_price = []
        for row in suggestions_sorted:
            precio = float(row['PRECIOB'])  # Empezamos con el precio base

            if precio_bonificado_var.get() == 1 and precio_iva_var.get() == 0:
                precio = float(math.ceil((precio * 1.3) / 10.0) * 10) 
            elif precio_iva_var.get() == 1 and precio_bonificado_var.get() == 0:
                precio = (precio * 1.21)  
            elif precio_iva_var.get() == 1 and precio_bonificado_var.get() == 1:
                precio = float(math.ceil((precio * 1.3) / 10.0) * 10) * 1.21

            suggestions_with_size_and_price.append(
                f"{row['NOMBRE']}--{row['ENVASE']} - ${precio:.2f}"
            )

        producto_entry['values'] = suggestions_with_size_and_price

        # Sugerencias con solo nombre y envase para autocompletar
        suggestions_with_size = [
            f"{row['NOMBRE']}--{row['ENVASE']}" 
            for row in suggestions_sorted
        ]

def autocomplete_cli(event=None):
    cli_text = cliente_entry.get().lower()
    # Now it will also match substrings in the 'RAZON' field
    suggestions2 = [row for row in clipro if cli_text in row['RAZON'].lower()]
    if suggestions2:
        cliente_entry.set('')  # Clear the current content
        suggestions2_sorted = sorted(suggestions2, key=lambda row: row['RAZON'])  # Sort the suggestions alphabetically
        cliente_entry['values'] = [row['RAZON'] for row in suggestions2_sorted]  # Set the new values
        cliente_entry.set(suggestions2_sorted[0]['RAZON'])  # Set the first suggestion as the current value


def robust_decode(bs):
    '''Intenta decodificar una cadena de bytes utilizando varias
codificaciones.'''
    for encoding in ('utf-8', 'latin-1', 'cp1252'):  # Añade aquí más codificaciones si es necesario
        try:
            return bs.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError('No se pudo decodificar la cadena de bytes')

def agregar_producto(event=None):
    try:
        global precio
        numero_fila = numero_fila_var.get()
        codigo_producto = codigo_var.get()
        
        # Obtener el valor de cantidad como float
        cantidad = float(cantidad_entry.get())
        
        # Determinar si la cantidad a mostrar debe ser int o float
        if cantidad.is_integer():
            cantidad_a_mostrar = int(cantidad)
        else:
            cantidad_a_mostrar = cantidad
            
        producto = producto_entry.get()
        tamaño = tamaño_entry.get()
        precio = float(precio_entry.get())
        
        # El cálculo se sigue haciendo con el float original para mantener la precisión
        total_producto = cantidad * precio

        # Opcional: Formatear también el total para un aspecto consistente
        if total_producto.is_integer():
            total_a_mostrar = int(total_producto)
        else:
            total_a_mostrar = round(total_producto, 2) # Redondear a 2 decimales por si acaso

        numero_fila = int(numero_fila) + 1
        numero_fila_var.set(numero_fila)
        
        # Insertar los valores con el formato deseado en el Treeview
        factura_treeview.insert('', 'end', values=(
            numero_fila, 
            codigo_producto, 
            producto, 
            tamaño, 
            cantidad_a_mostrar,  # Usar la variable formateada
            precio, 
            total_a_mostrar,     # Usar la variable formateada
            numero_fila
        ))
        
        calcular_total()
        precio_entry.delete(0, tk.END)
        existencia_entry.delete(0, tk.END)
        producto_entry.delete(0, tk.END)
        cantidad_entry.delete(0, tk.END)
        tamaño_entry.delete(0, tk.END)
        producto_entry.focus_set()
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce un número válido")

def calcular_total():
    total = 0.0
    totalisimo = 0.0
    pagoe = 0.0
    pagoch = 0.0
    saldo = acreedor_deudor_var.get()
    saldo = '0' if saldo == '' else saldo
    saldot = 0.0
    pagod = 0.0
    dolprom = 0.0
    for child in factura_treeview.get_children():
        total += float(factura_treeview.item(child, 'values')[6])
    total_label.config(text=f"Subtotal: {total}")
    totalisimo = round(float(total) - float(saldo), 2)
    totalisimo_label.config(text=f"Total: {totalisimo}")
    dolprom = dolar_var.get() # get the average of the current U$D to ARS rate 
    pagod = dolar_pag.get() # Added for using U$D currency
    pagod = '0' if pagod == '' else pagod
    pagodars = float(dolprom) * float(pagod) # convert to ARS
    pagoe = efectivo_var.get() # Get value from efectivo_var
    pagoch = cheque_var.get() # Get value from cheque_var
    pagoe = '0' if pagoe == '' else pagoe
    pagoch = '0' if pagoch == '' else pagoch
    pagodars = '0' if pagodars == '' else pagodars
    pagot = float(pagoe) + float (pagoch) + float (pagodars)
    saldot = round(-float(totalisimo) + float(pagot), 2)
    saldo_final_label.config(text=f"Saldo final: {saldot}")
    return totalisimo
    
def borrar_fila(event):
    selected = factura_treeview.selection()  # Obtener los items seleccionados
    numero_fila = numero_fila_var.get()
    numero_fila -= 1
    numero_fila_var.set(numero_fila)
    for item in selected:
        factura_treeview.delete(item)  # Eliminar el item del Treeview
    calcular_total()


import subprocess

import dbf

def actualizar_stock():
    print("Ejecutando actualizar_stock")
    global stock
    stock_updates = {}
    for row in factura_treeview.get_children():
        values = factura_treeview.item(row, 'values')
        codigo = values[1]
        cantidad = float(values[4])
        if codigo in stock_updates:
            stock_updates[codigo] -= cantidad
        else:
            stock_updates[codigo] = -cantidad
            
    dbfpath = 'STOCK1.DBF' 
    table = dbf.Table(dbfpath) 
    with table:  
        for record in table:
            codigo = record['CODIGO'].strip()
            if codigo in stock_updates:
                # Usar with para modificar el registro
                with record as r:
                    r['EXISTENCIA'] = r['EXISTENCIA'] + stock_updates[codigo]
                
def create_and_print_invoice():
    campo_escrito = acreedor_deudor_var.get()
    if not campo_escrito or '0.0' in campo_escrito:
        update_client()

    output_folder = r"C:\Users\OEM\Documents\BOLETAS" 
    
    # Check if folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_name = cliente_entry.get() + " " + "PX" + boleta_entry.get() + ".pdf"
    # Combine folder and filename
    pdf_path = os.path.join(output_folder, pdf_name)
    # Crear un nuevo PDF con el tamaño de página A4

    
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
                y -=7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -=7
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
                y -=7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -=7
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

        y -=7

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

    ####### DUPLICADO

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
                y -=7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -=7
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
                y -=7
                c.drawRightString(left_margin + 280, y, "Suma de la pagina: {:.2f}".format(suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Suma de paginas anteriores: {:.2f}".format(suma_total - suma))
                y -= 13
                c.drawRightString(left_margin + 280, y, "Subtotal: {:.2f}".format(suma_total))

            else:
                y -=7
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

        y -=7

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

def print_pdf(pdf_path):
    # Obtiene la impresora predeterminada
    printer_name = win32print.GetDefaultPrinter()

    # Lanza un proceso para imprimir el PDF
    win32api.ShellExecute(0, "print", pdf_path, '/d:"%s"' % printer_name, ".", 0)


def open_invoice():
    global action
    try:
        
        pdf_path = create_and_print_invoice()
        # Abrir el PDF con el lector de PDF predeterminado
        subprocess.Popen([pdf_path], shell=True)
    except OSError as e:
        # Si el archivo está en uso por otro proceso, se lanzará una excepción OSError.
        messagebox.showerror("Error al imprimir", 
                             "No se pudo abrir porque está abierta la boleta en el lector\nde PDF (icono rojo) o esta abierto el programa del vivero")
    except Exception as e:
        # Capturar cualquier otra excepción inesperada
        messagebox.showerror("Error inesperado", f"Ha ocurrido un error inesperado: {e}")

    


def print_invoice():
    global action
    try:
        
        pdf_path = create_and_print_invoice()

        # Print the file located at that specific path
        os.startfile(pdf_path, "print")

    except OSError as e:
        # Si el archivo está en uso por otro proceso, se lanzará una excepción OSError.
        messagebox.showerror("Error al abrir el PDF", 
                             "No se pudo imprimir porque está abierta la boleta en el lector\nde PDF (icono rojo) o esta abierto el programa del vivero")
    except Exception as e:
        # Capturar cualquier otra excepción inesperada
        messagebox.showerror("Error inesperado", f"Ha ocurrido un error inesperado: {e}")

    
import os
import shutil
from dbfread import DBF

current_dir = os.path.dirname(os.path.realpath(__file__))

# Lista de archivos DBF
dbf_files = ['STOCK1.DBF', 'CLIPRO.DBF', 'PROVE.DBF']
dbf_objects = []

for dbf_file in dbf_files:
    original_dbf_file = os.path.join(current_dir, dbf_file)
    temp_dbf_file = os.path.join(current_dir, f'temp_{dbf_file}')

    # Abrir y leer la copia temporal dentro de un bloque 'with'
    with DBF(original_dbf_file, encoding='cp850') as db:
        dbf_objects.append(db.records)  # Guarda los registros, no el objeto DBF

    # Ahora que el objeto DBF está cerrado, se puede copiar el archivo
    shutil.copyfile(original_dbf_file, temp_dbf_file)

# Ahora dbf_objects contiene una lista de listas de registros

# Ahora dbf_objects contiene los objetos DBF de los archivos temporales
stock, clipro, prove = dbf_objects

cliente_label = tk.Label(window, text="Nombre del Cliente")
cliente_label.grid(row=0, column=3)

cliente_var = tk.StringVar()  # Create a StringVar instance

def update_title(*args):  # Function to update window title
    window.title(cliente_var.get())

cliente_var.trace('w', update_title)

cliente_entry = ttk.Combobox(window, textvariable=cliente_var, postcommand=autocomplete_cli)
cliente_entry.configure(font=('Arial', 13))
cliente_entry.grid(row=1, column=3)


boleta_label = tk.Label(window, text="Boleta")
boleta_label.grid(row=0, column=4)
boleta_entry = tk.Entry(window)
boleta_entry.configure(font=('Arial', 13))
boleta_entry.grid(row=1, column=4)

cuit_label = tk.Label(window, text="CUIT")
cuit_label.grid(row=0, column=1)
cuit_entry = tk.Entry(window, textvariable=CUIT_var)
cuit_entry.configure(font=('Arial', 13))
cuit_entry.grid(row=1, column=1)

numero_label = tk.Label(window, text="Numero de cliente")
numero_label.grid(row=0, column=2)
numero_entry = tk.Entry(window, textvariable=numero_var)
numero_entry.configure(font=('Arial', 13))
numero_entry.grid(row=1, column=2)

codi_label = tk.Label(window, text="codigo")
codi_label.grid(row=2, column=1)
codi_entry = ttk.Combobox(window, textvariable=codigo_var)
codi_entry.configure(font=('Arial', 13))
codi_entry.grid(row=3, column=1)

producto_label = tk.Label(window, text="Producto")
producto_label.grid(row=2, column=3)
producto_entry = ttk.Combobox(window, postcommand=autocomplete, width=75)
producto_entry.configure(font=('Arial', 13))
producto_entry.grid(row=3, column=2, columnspan=3)

existencia_label = tk.Label(window, text="Stock")
existencia_label.grid(row=4, column=2)
existencia_entry = tk.Entry(window, textvariable=existencias_var)
existencia_entry.configure(font=('Arial', 13))
existencia_entry.grid(row=5, column=2)

tamaño_label = tk.Label(window, text="Tamaño")
tamaño_label.grid(row=4, column=3)
tamaño_entry = tk.Entry(window, textvariable=TAMAÑO_var)
tamaño_entry.configure(font=('Arial', 13))
tamaño_entry.grid(row=5, column=3)

def update_client():
    # Obtiene el producto seleccionado
    selected_client = cliente_var.get()

    # Busca el producto seleccionado en el stock y actualiza el precio
    for row in clipro:
        if row['RAZON'] == selected_client:
            numero_var.set(row['NUMERO'])
            acreedor_var.set(row['ACREEDOR'])
            deudor_var.set(row['DEUDOR'])
            CUIT_var.set(row['NCUIT'])
            acreedor_deudor_var.set( round( float( acreedor_var.get() ) - float( deudor_var.get() ), 2 ) ) #esperemos que esto lo arregle
            break

def on_product_selection(event):
    campo_escrito = acreedor_deudor_var.get()
    if not campo_escrito or '0.0' in campo_escrito:
        update_client()
    global precio, precio_original
    # Obtiene el producto seleccionado
    selected_product = producto_entry.get().split(" - ")[0]
    producto_entry.set(selected_product)

    # Divide la cadena seleccionada en el nombre del producto y su tamaño
    selected_name, selected_size = selected_product.split('--', 1)

    # Busca el producto seleccionado en el stock y actualiza el precio
    for row in stock:
        if row['NOMBRE'] == selected_name and row['ENVASE'] == selected_size:
            precio_original = float(row['PRECIOB'])
            precio = precio_original
            # print(f"precio_original: {precio_original}")  # Impresión de depuración
            if precio_bonificado_var.get() == 1:
                precio = float(math.ceil((float(precio_original) * 1.3) / 10.0) * 10)  # Aumenta el precio en un 30% y redondea a la decena más cercana
            if precio_iva_var.get() == 1:
                precio = (float(precio_original*100) * 1.21)/100 # Aumenta el precio en un 21%
            if precio_iva_var.get() == 1 and precio_bonificado_var.get() == 1:
                precio = (float(math.ceil((float(precio_original) * 1.3) / 10.0) * 10) * 121) / 100  # Aumenta el precio en un 30% y redondea a la decena más cercana
            PRECIOB_var.set(precio)
            codigo_var.set(row['CODIGO'])
            existencias_var.set(row['EXISTENCIA'])
            TAMAÑO_var.set(row['ENVASE'])
            break
    cantidad_entry.focus_set()

def on_checkbox_change():
    global precio
    if precio_bonificado_var.get() == 1 and precio_iva_var.get() == 0:
        precio = float(math.ceil((float(precio_original) * 1.3) / 10.0) * 10)  # Aumenta el precio en un 30% y redondea a la decena más cercana
    elif precio_iva_var.get() == 1 and precio_bonificado_var.get() == 0:
         #precio = float(precio_original) * 1.21
        precio = (float(precio_original*100) * 1.21)/100 # Aumenta el precio en un 21%  # Aumenta el precio en un 30% y redondea a la decena más cercana
    elif precio_iva_var.get() == 1 and precio_bonificado_var.get() == 1:
        precio = float(math.ceil((float(precio_original) * 1.3) / 10.0) * 10) * 1.21  # Aumenta el precio en un 30% y redondea a la decena más cercana
    else:
        precio = precio_original  # Restaura el precio original
    # print(f"precio: {precio}")  # Impresión de depuración
    PRECIOB_var.set(precio)

# Vincula el evento de selección de la lista de sugerencias a la función on_product_selection
producto_entry.bind('<<ComboboxSelected>>', on_product_selection)

cantidad_label = tk.Label(window, text="Cantidad")
cantidad_label.grid(row=6, column=3)
cantidad_entry = tk.Entry(window)
cantidad_entry.configure(font=('Arial', 13))
cantidad_entry.grid(row=7, column=3)
cantidad_entry.bind('<Return>', agregar_producto)

var = tk.IntVar()
var.trace('w', update_price)

precio_label = tk.Label(window, text="Precio por unidad")
precio_label.grid(row=4, column=4)
precio_entry = tk.Entry(window, textvariable=PRECIOB_var)
precio_entry.configure(font=('Arial', 13))
precio_entry.grid(row=5, column=4)

checkbox = tk.Checkbutton(window, text='Publico',
variable=precio_bonificado_var, command=on_checkbox_change)
checkbox.grid(row=5, column=5)

checkboxiva = tk.Checkbutton(window, text='IVA',
variable=precio_iva_var, command=on_checkbox_change)
checkboxiva.grid(row=6, column=5)

acreedor_deudor_label = tk.Label(window, text="Saldo anterior")
acreedor_deudor_label.grid(row=9, column=4)
acreedor_deudor_entry = tk.Entry(window, textvariable=acreedor_deudor_var) #Have to round the value to 2 decimal places
acreedor_deudor_entry.configure(font=('Arial', 13))
acreedor_deudor_var.trace("w", lambda name, index, mode, sv=acreedor_deudor_var: calcular_total())
acreedor_deudor_entry.grid(row=10, column=4)

efectivo_label = tk.Label(window, text="Efectivo")
efectivo_label.grid(row=9, column=2)
efectivo_entry = tk.Entry(window, textvariable=efectivo_var)
efectivo_entry.configure(font=('Arial', 13))
efectivo_var.trace("w", lambda name, index, mode, sv=efectivo_var: calcular_total())
efectivo_entry.grid(row=10, column=2)

cheque_label = tk.Label(window, text="Cheque")
cheque_label.grid(row=9, column=1)
cheque_entry = tk.Entry(window, textvariable=cheque_var)
cheque_entry.configure(font=('Arial', 13))
cheque_var.trace("w", lambda name, index, mode, sv=cheque_var: calcular_total())
cheque_entry.grid(row=10, column=1)

def on_client_selection(event):
    # Obtiene el producto seleccionado
    selected_client = cliente_entry.get()

    # Busca el producto seleccionado en el stock y actualiza el precio
    for row in clipro:
        if row['RAZON'] == selected_client:
            numero_var.set(row['NUMERO'])
            acreedor_var.set(row['ACREEDOR'])
            deudor_var.set(row['DEUDOR'])
            CUIT_var.set(row['NCUIT'])
            acreedor_deudor_var.set( round( float(acreedor_var.get()) - float(deudor_var.get()), 2) )
            break
    producto_entry.focus_set()

# Vincula el evento de selección de la lista de sugerencias a la función on_product_selection
cliente_entry.bind('<<ComboboxSelected>>', on_client_selection)

agregar_button = tk.Button(window, text="Agregar", command=agregar_producto)
agregar_button.grid(row=10, column=3)

style = ttk.Style()
style.configure("mystyle.Treeview", font=('Arial', 13))  # sets the font size for the content to 13
style.configure("mystyle.Treeview.Heading", font=('Arial', 15, 'bold'))  # sets the font size for the headings to 15 and makes them bold

factura_treeview = ttk.Treeview(window, columns=('Fila', 'Codigo', 'Producto', 'Tamaño', 'Cantidad', 'Precio', 'Total'), show='headings', style="mystyle.Treeview")
factura_treeview.column('Codigo', width=150)
factura_treeview.column('Producto', width=500)
factura_treeview.column('Tamaño', width=100)
factura_treeview.column('Cantidad', width=150)
factura_treeview.column('Precio', width=150)
factura_treeview.column('Total', width=150)
factura_treeview.column('Fila', width=40) 
factura_treeview.heading('Fila', text='Fila')
factura_treeview.heading('Codigo', text='Codigo')
factura_treeview.heading('Producto', text='Producto')
factura_treeview.heading('Tamaño', text='Tamaño')
factura_treeview.heading('Cantidad', text='Cantidad')
factura_treeview.heading('Precio', text='Precio')
factura_treeview.heading('Total', text='Total')
factura_treeview.grid(row=11, column=0, columnspan=6)
scrollbar = ttk.Scrollbar(window, orient="vertical", command=factura_treeview.yview)
scrollbar.grid(row=11, column=7, sticky="ns")
factura_treeview.configure(yscrollcommand=scrollbar.set)
factura_treeview.bind('<Delete>', borrar_fila)

factura_treeview.grid(row=11, column=0, columnspan=6, sticky="nsew")
scrollbar.grid(row=11, column=7, sticky="ns")

window.grid_rowconfigure(11, weight=1)
window.grid_columnconfigure(3, weight=1)

def editar_fila(event):
    """Opens a popup for editing the selected row."""
    item = factura_treeview.selection()
    if item:
        # Get values from selected row
        values = factura_treeview.item(item, "values")
        fila, codigo, producto, tamaño, cantidad, precio, total, dummy = values

        # Create popup window
        popup = tk.Toplevel(window)
        popup.title("Editar Fila")

        # Labels and entry fields
        labels = ["fila", "Código:", "Producto:", "Tamaño:", "Cantidad:", "Precio:"]
        entries = []
        for i, label_text in enumerate(labels):
            label = ttk.Label(popup, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(popup)
            entry.insert(0, values[i])  # Populate entry with current value
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        # Update button
        def update_row():
            new_fila = entries[0].get()
            new_codigo = entries[1].get()
            new_producto = entries[2].get()
            new_tamaño = entries[3].get()
            new_cantidad = entries[4].get()
            new_precio = entries[5].get()
            
            # Calculate total and fila
            new_total = str(float(new_cantidad) * float(new_precio))

            # Update values in treeview
            factura_treeview.item(item, values=(new_fila, new_codigo, new_producto, new_tamaño, new_cantidad, new_precio, new_total, dummy))
            popup.destroy()
            calcular_total()

        update_button = ttk.Button(popup, text="Actualizar", command=update_row)
        update_button.grid(row=6, column=0, columnspan=2, pady=10)

# Bind double-click to edit row
factura_treeview.bind('<Double-Button-1>', editar_fila)

dolares_entry = tk.Entry(window, textvariable=dolar_pag)
dolares_entry.configure(font=('Arial', 13))
dolar_pag.trace("w", lambda name, index, mode, sv=dolar_pag: calcular_total())
dolares_entry.grid(row=13, column=1)

total_label = tk.Label(window, text="Subtotal: 0")
total_label.configure(font=('Arial', 15))
total_label.grid(row=12, column=3)

totalisimo_label = tk.Label(window, text="Total: 0")
totalisimo_label.configure(font=('Arial', 15))
totalisimo_label.grid(row=12, column=4)

saldo_final_label = tk.Label(window, text="Saldo final: 0")
saldo_final_label.configure(font=('Arial', 15))
saldo_final_label.grid(row=12, column=5)

button_buscar = tk.Button(window, text="En dolares", command=buscar_valor)
button_buscar.grid(row=13, column=2)

print_button = tk.Button(window, text="Imprimir boleta", command=print_invoice)
print_button.grid(row=13, column=5)

open_button = tk.Button(window, text="Ver PDF", command=open_invoice)
open_button.grid(row=13, column=4)


window.mainloop()
