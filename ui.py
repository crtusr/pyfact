import tkinter as tk
from tkinter.font import Font
from tkinter import ttk, messagebox
from tkinter import Grid
from dataclasses import dataclass, field
import logic
import data as db
import os
import subprocess
import pdf_io
import web_scraping as web
import traceback
import config


@dataclass
class app_state:
    PRECIOB_var: tk.StringVar = None
    precio_bonificado_var: tk.IntVar = None
    precio_iva_var: tk.IntVar = None
    TAMAÑO_var: tk.StringVar = None
    numero_var: tk.StringVar = None
    acreedor_var: tk.StringVar = None
    deudor_var: tk.StringVar = None
    acreedor_deudor_var: tk.StringVar = None
    existencias_var: tk.StringVar = None
    codigo_var: tk.StringVar = None
    efectivo_var: tk.StringVar = None
    cheque_var: tk.StringVar = None
    CUIT_var: tk.StringVar = None
    dolar_var: tk.StringVar = None
    dolar_pag: tk.StringVar = None
    cliente_var: tk.StringVar = None
    precio_original: int = 0  # necessary for the persistence of base price


@dataclass
class context:
    numero_fila_var: tk.IntVar = None
    reset_button: tk.Button = None
    cliente_label: tk.Label = None
    cliente_entry: tk.Entry = None
    boleta_label: tk.Label = None
    boleta_entry: tk.Entry = None
    cuit_label: tk.Label = None
    cuit_entry: tk.Entry = None
    numero_label: tk.Label = None
    numero_entry: tk.Entry = None
    codi_label: tk.Label = None
    codi_entry: tk.Entry = None
    producto_label: tk.Label = None
    producto_entry: tk.Entry = None
    existencia_label: tk.Label = None
    existencia_entry: tk.Entry = None
    tamaño_label: tk.Label = None
    tamaño_entry: tk.Entry = None
    cantidad_label: tk.Label = None
    cantidad_entry: tk.Entry = None
    precio_label: tk.Label = None
    precio_entry: tk.Entry = None
    checkbox: tk.Checkbutton = None
    checkboxiva: tk.Checkbutton = None
    acreedor_deudor_label: tk.Label = None
    acreedor_deudor_entry: tk.Entry = None
    efectivo_label: tk.Label = None
    efectivo_entry: tk.Entry = None
    cheque_label: tk.Label = None
    cheque_entry: tk.Entry = None
    agregar_button: tk.Button = None
    style: ttk.Style = None
    factura_treeview: ttk.Treeview = None
    scrollbar: ttk.Scrollbar = None
    dolares_entry: tk.Entry = None
    total_label: tk.Label = None
    totalisimo_label: tk.Label = None
    saldo_final: tk.Label = None
    button_buscar: tk.Button = None
    print_button: tk.Button = None
    open_button: tk.Button = None


def custom_report_callback_exception(exc, val, tb):
    traceback.print_exception(tb, val, exc)


def set_global_config(popup, entries):
    # should look for a way to avoid changing globals
    config.IVA = (float(entries[0].get())/100.0) + 1
    config.recargo = (float(entries[1].get())/100.0) + 1
    config.redondeo = float(entries[2].get())
    popup.destroy()


def configuration(window):
    popup = tk.Toplevel(window)
    popup.title("Configuración")

    # Labels and entry fields
    labels = ["IVA",
              "Publico:",
              "Redondear a:"]
    values = [config.IVA, config.recargo, config.redondeo]
    entries = []
    for i, label_text in enumerate(labels):
        label = ttk.Label(popup, text=label_text)
        label.configure(font=('Arial', 13))
        label.grid(row=i, column=0, padx=5, pady=5)
        entry = ttk.Entry(popup)
        if i < 2:
            entry.insert(0, (values[i] * 100.0) - 100)  # Populate entry
        else:
            entry.insert(0, values[i])  # Populate entry with current value
        entry.configure(font=('Arial', 13))
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    accept_button = ttk.Button(
            popup,
            text="Aceptar",
            command=lambda: set_global_config(popup, entries))
    accept_button.grid(row=6, column=0, columnspan=2, pady=10)
    return


def editar_fila(window, ui, state, event):
    """Opens a popup for editing the selected row."""
    item = ui.factura_treeview.selection()
    if item:
        # Get values from selected row
        values = ui.factura_treeview.item(item, "values")
        fila, codigo, producto, tamaño, cantidad, precio, total, dummy = values
        print(values)
        # Create popup window
        popup = tk.Toplevel(window)
        popup.title("Editar Fila")

        # Labels and entry fields
        labels = ["fila",
                  "Código:",
                  "Producto:",
                  "Tamaño:",
                  "Cantidad:",
                  "Precio:"]
        entries = []
        for i, label_text in enumerate(labels):
            label = ttk.Label(popup, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(popup)
            entry.insert(0, values[i])  # Populate entry with current value
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        # Update button
            logic.calcular_total(ui, state)

        entries.append(dummy)
        # I dont know what this dummy is but I'll do it to pass it to update
        update_button = ttk.Button(
                popup,
                text="Actualizar",
                command=lambda: update_row(popup, ui, entries, item))
        update_button.grid(row=6, column=0, columnspan=2, pady=10)


def update_row(popup, ui_context, entries, item):
    new_fila = entries[0].get()
    new_codigo = entries[1].get()
    new_producto = entries[2].get()
    new_tamaño = entries[3].get()
    new_cantidad = entries[4].get()
    new_precio = entries[5].get()

    # Calculate total and fila
    new_total = str(float(new_cantidad) * float(new_precio))

    # Update values in treeview
    ui_context.factura_treeview.item(
            item,
            values=(
                new_fila,
                new_codigo,
                new_producto,
                new_tamaño,
                new_cantidad,
                new_precio,
                new_total,
                entries[6]))  # should be last values[x]
    popup.destroy()


def init_state():
    tk_state = app_state()

    tk_state.PRECIOB_var = tk.StringVar()
    tk_state.precio_bonificado_var = tk.IntVar()
    tk_state.precio_iva_var = tk.IntVar()
    tk_state.TAMAÑO_var = tk.StringVar()
    tk_state.numero_var = tk.StringVar()
    tk_state.acreedor_var = tk.StringVar()
    tk_state.deudor_var = tk.StringVar()
    tk_state.acreedor_deudor_var = tk.StringVar()
    tk_state.existencias_var = tk.StringVar()
    tk_state.codigo_var = tk.StringVar()
    tk_state.efectivo_var = tk.StringVar()
    tk_state.cheque_var = tk.StringVar()
    tk_state.CUIT_var = tk.StringVar()
    tk_state.dolar_var = tk.StringVar(value='0.0')
    tk_state.dolar_pag = tk.StringVar(value='0.0')
    tk_state.cliente_var = tk.StringVar()

    return tk_state


def reset_program(ui, state):
    ui.producto_entry.delete(0, 'end')
    ui.cliente_entry.delete(0, 'end')
    ui.cantidad_entry.delete(0, 'end')
    ui.precio_entry.delete(0, tk.END)
    ui.existencia_entry.delete(0, tk.END)
    ui.producto_entry.delete(0, tk.END)
    ui.cantidad_entry.delete(0, tk.END)
    ui.tamaño_entry.delete(0, tk.END)
    ui.cliente_entry.delete(0, tk.END)
    ui.boleta_entry.delete(0, tk.END)
    ui.codi_entry.delete(0, tk.END)
    ui.acreedor_deudor_entry.delete(0, tk.END)
    ui.efectivo_entry.delete(0, tk.END)
    ui.cheque_entry.delete(0, tk.END)
    ui.numero_entry.delete(0, tk.END)
    ui.cuit_entry.delete(0, tk.END)
    ui.dolares_entry.delete(0, tk.END)
    ui.numero_fila_var.set(0)
    ui.cliente_entry.focus_set()

    # Clear the Treeview
    for item in ui.factura_treeview.get_children():
        ui.factura_treeview.delete(item)

    logic.calcular_total(ui, state)


def autocomplete(producto_entry, stock, state, event=None):
    srch = producto_entry.get().lower()
    suggestions = [row for row in stock if srch in row['NOMBRE'].lower()]
    if suggestions:
        suggestions_sorted = sorted(suggestions, key=lambda row: row['NOMBRE'])

        suggestions_with_size_and_price = []
        for row in suggestions_sorted:
            precio = float(row['PRECIOB'])  # Base price
            es_publico = state.precio_bonificado_var.get()
            tiene_IVA = state.precio_iva_var.get()

            if es_publico == 1 and tiene_IVA == 0:
                precio = logic.public_price(precio)
            elif tiene_IVA == 1 and es_publico == 0:
                precio = logic.add_IVA(precio)
            elif tiene_IVA == 1 and es_publico == 1:
                precio = logic.add_IVA(logic.public_price(precio))

            suggestions_with_size_and_price.append(
                f"{row['NOMBRE']}--{row['ENVASE']} - ${precio:.2f}"
            )

        producto_entry['values'] = suggestions_with_size_and_price

        # Sugerencias con solo nombre y envase para autocompletar
        # suggestions_with_size = [
        #     f"{row['NOMBRE']}--{row['ENVASE']}"
        #     for row in suggestions_sorted
        # ]


def autocomplete_cli(cli_entry, clipro, fields, event=None):
    cp = cli_entry.get().lower()
    # Now it will also match substrings in the 'RAZON' field
    suggestions = [row for row in clipro if cp in row[fields['razon']].lower()]
    if suggestions:
        cli_entry.set('')  # Clear the current content
        suggestions_sorted = sorted(
                suggestions,
                key=lambda row: row[fields['razon']])
        cli_entry['values'] = [
                row[fields['razon']]
                for row
                in suggestions_sorted]
        cli_entry.set(suggestions_sorted[0][fields['razon']])


def get_entries_for_billing(ui):
    products = []
    for index in ui.factura_treeview.get_children():
        elem = ui.factura_treeview.item(index, 'values')
        products.append([elem[2], elem[4], elem[5]])
    return products


def get_prod_entries_row(ui, index):
    return ui.factura_treeview.item(index, 'values')


def get_prod_entries_indexes(ui):
    return ui.factura_treeview.get_children()


def get_prod_entry_price(ui, index):
    return float(ui.factura_treeview.item(index, 'values')[6])


def sum_column_from_ui_table(ui, col):
    total = 0
    for child in ui.factura_treeview.get_children():
        total += float(ui.factura_treeview.item(child, 'values')[col])
    return total


def update_bill_sum(ui, totales):
    # 0 = subtotal; 1 = total a pagar; 2 = saldo final
    ui.total_label.config(text=f"Subtotal: {totales[0]}")
    ui.totalisimo_label.config(text=f"Total: {totales[1]}")
    ui.saldo_final_label.config(text=f"Saldo final: {totales[2]}")
    return


def agregar_producto(ui, state, event=None):
    try:
        #   global precio
        numero_fila = ui.numero_fila_var.get()
        codigo_producto = state.codigo_var.get()

        # Obtener el valor de cantidad como float
        cantidad = float(ui.cantidad_entry.get())

        # Determinar si la cantidad a mostrar debe ser int o float
        if cantidad.is_integer():
            cantidad_a_mostrar = int(cantidad)
        else:
            cantidad_a_mostrar = cantidad

        producto = ui.producto_entry.get()
        tamaño = ui.tamaño_entry.get()
        precio = float(ui.precio_entry.get())

        total_producto = cantidad * precio

        if total_producto.is_integer():
            total_a_mostrar = int(total_producto)
        else:
            total_a_mostrar = round(total_producto, 2)

        numero_fila = int(numero_fila) + 1
        ui.numero_fila_var.set(numero_fila)

        # Insertar los valores con el formato deseado en el Treeview
        ui.factura_treeview.insert('', 'end', values=(
            numero_fila,
            codigo_producto,
            producto,
            tamaño,
            cantidad_a_mostrar,  # Formatted var
            precio,
            total_a_mostrar,     # Formatted var
            numero_fila
        ))

        logic.calcular_total(ui, state)
        ui.precio_entry.delete(0, tk.END)
        ui.existencia_entry.delete(0, tk.END)
        ui.producto_entry.delete(0, tk.END)
        ui.cantidad_entry.delete(0, tk.END)
        ui.tamaño_entry.delete(0, tk.END)
        ui.producto_entry.focus_set()
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce un número válido")


def borrar_fila(ui, state, event):
    selected = ui.factura_treeview.selection()
    numero_fila = ui.numero_fila_var.get()
    numero_fila -= 1
    ui.numero_fila_var.set(numero_fila)
    for item in selected:
        ui.factura_treeview.delete(item)
    logic.calcular_total(ui, state)


def show_message(title, message):
    messagebox.showinfo(title, message)


def show_error(title, message):
    messagebox.showerror(title, message)


def update_client(state):
    # Obtiene el producto seleccionado
    selected_client = state.cliente_var.get()
    if selected_client == '':
        state.numero_var.set('999')
        return


def open_invoice(ui, state, data):
    global action
    try:

        pdf_path = pdf_io.create_and_print_invoice(ui, state)
        campo_escrito = state.acreedor_deudor_var.get()
        if not campo_escrito or '0.0' in campo_escrito:
            update_client(state)

# Abrir el PDF con el lector de PDF predeterminado
        subprocess.Popen([pdf_path], shell=True)

        db.actualizar_stock(data, ui)
    except OSError as e:
        messagebox.showerror(
                "Error al imprimir: {e}",
                "No se pudo abrir porque está abierta la boleta" +
                "en el lector\nde PDF (icono rojo) o esta" +
                f"abierto el programa del vivero:\n{e}")
    except Exception as e:
        # Capturar cualquier otra excepción inesperada
        messagebox.showerror(
                "Error inesperado",
                f"Ha ocurrido un error inesperado: {e}")


def print_invoice(ui, state, data):
    global action  # seems like dead code
    try:

        pdf_path = pdf_io.create_and_print_invoice(ui, state)

        campo_escrito = state.acreedor_deudor_var.get()
        if not campo_escrito or '0.0' in campo_escrito:
            update_client(state)
        # Print the file located at that specific path
        os.startfile(pdf_path, "print")

        db.actualizar_stock(data, ui)

    except OSError as e:
        messagebox.showerror(
                "Error al abrir el PDF",
                "No se pudo imprimir porque está abierta la boleta en el " +
                "lector\nde PDF (icono rojo) o esta abierto el programa del " +
                f"vivero:\n{e}")
    except Exception as e:
        # En caso de otra excepción inesperada
        messagebox.showerror(
                "Error inesperado",
                f"Ha ocurrido un error inesperado: {e}")


def update_title(window, current_title, *args):
    window.title(current_title)


def cantidad_de_plantas(ui):
    total = 0
    for child in ui.factura_treeview.get_children():
        total += float(ui.factura_treeview.item(child, 'values')[4])
    return total


def on_product_selection(state, ui, stock, event):
    campo_escrito = state.acreedor_deudor_var.get()
    if not campo_escrito or '0.0' in campo_escrito:
        update_client(state)

    selected_product = ui.producto_entry.get().split(" - ")[0]
    ui.producto_entry.set(selected_product)

    selected_name, selected_size = selected_product.split('--', 1)

    for row in stock:
        if row['NOMBRE'] == selected_name and row['ENVASE'] == selected_size:
            state.precio_original = float(row['PRECIOB'])
            precio = logic.decide_price(
                    state.precio_original,
                    state.precio_bonificado_var.get(),
                    state.precio_iva_var.get())

            state.PRECIOB_var.set(precio)
            state.codigo_var.set(row['CODIGO'])
            state.existencias_var.set(row['EXISTENCIA'])
            state.TAMAÑO_var.set(row['ENVASE'])
            break
    ui.cantidad_entry.focus_set()


def on_checkbox_change(state):
    precio = logic.decide_price(
            state.precio_original,
            state.precio_bonificado_var.get(),
            state.precio_iva_var.get())
    # print(f"precio: {precio}")  # debug print
    state.PRECIOB_var.set(precio)


def on_client_selection(ui, state, data, event):
    selected_client = ui.cliente_entry.get()

    for row in data.clipro:
        if row[data.fields['razon']] == selected_client:
            state.numero_var.set(row[data.fields['numero']])
            state.acreedor_var.set(row[data.fields['acreedor']])
            state.deudor_var.set(row[data.fields['deudor']])
            state.CUIT_var.set(row[data.fields['ncuit']])
            state.acreedor_deudor_var.set(round(
                float(state.acreedor_var.get()) -
                float(state.deudor_var.get()),
                2))
            break
    ui.producto_entry.focus_set()


def init(data):
    window = tk.Tk()

    # window.report_callback_exception = custom_report_callback_exception

    state = init_state()
    ui = context()

    arial_font = Font(family='Arial', size=13)

# Change the font for all Listboxes that are part of a Combobox
    window.option_add("*TCombobox*Listbox*Font", arial_font)

    window.title("Facturador")

    ui.numero_fila_var = tk.IntVar()
    ui.reset_button = tk.Button(
            window,
            text="Nueva boleta",
            command=lambda: reset_program(ui, state))
    ui.reset_button.grid(row=0, column=5)

    ui.config_button = tk.Button(
            window,
            text="Configuración",
            command=lambda: configuration(window))
    ui.config_button.grid(row=7, column=5)

    ui.cliente_label = tk.Label(window, text="Nombre del Cliente")
    ui.cliente_label.grid(row=0, column=3)
    state.cliente_var.trace(
            'w',
            lambda *args: update_title(window, state.cliente_var.get(), *args))

    ui.cliente_entry = ttk.Combobox(
            window,
            textvariable=state.cliente_var,
            postcommand=lambda: autocomplete_cli(
                ui.cliente_entry,
                data.clipro,
                data.fields))
    ui.cliente_entry.configure(font=('Arial', 13))
    ui.cliente_entry.grid(row=1, column=3)

    ui.boleta_label = tk.Label(window, text="Boleta")
    ui.boleta_label.grid(row=0, column=4)
    ui.boleta_entry = tk.Entry(window)
    ui.boleta_entry.configure(font=('Arial', 13))
    ui.boleta_entry.grid(row=1, column=4)

    ui.cuit_label = tk.Label(window, text="CUIT")
    ui.cuit_label.grid(row=0, column=1)
    ui.cuit_entry = tk.Entry(window, textvariable=state.CUIT_var)
    ui.cuit_entry.configure(font=('Arial', 13))
    ui.cuit_entry.grid(row=1, column=1)

    ui.numero_label = tk.Label(window, text="Numero de cliente")
    ui.numero_label.grid(row=0, column=2)
    ui.numero_entry = tk.Entry(window, textvariable=state.numero_var)
    ui.numero_entry.configure(font=('Arial', 13))
    ui.numero_entry.grid(row=1, column=2)

    ui.codi_label = tk.Label(window, text="codigo")
    ui.codi_label.grid(row=2, column=1)
    ui.codi_entry = ttk.Combobox(window, textvariable=state.codigo_var)
    ui.codi_entry.configure(font=('Arial', 13))
    ui.codi_entry.grid(row=3, column=1)

    ui.producto_label = tk.Label(window, text="Producto")
    ui.producto_label.grid(row=2, column=3)
    ui.producto_entry = ttk.Combobox(
            window,
            postcommand=lambda: autocomplete(
                ui.producto_entry,
                data.stock,
                state),
            width=75)
    ui.producto_entry.configure(font=('Arial', 13))
    ui.producto_entry.grid(row=3, column=2, columnspan=3)

    ui.existencia_label = tk.Label(window, text="Stock")
    ui.existencia_label.grid(row=4, column=2)
    ui.existencia_entry = tk.Entry(window, textvariable=state.existencias_var)
    ui.existencia_entry.configure(font=('Arial', 13))
    ui.existencia_entry.grid(row=5, column=2)

    ui.tamaño_label = tk.Label(window, text="Tamaño")
    ui.tamaño_label.grid(row=4, column=3)
    ui.tamaño_entry = tk.Entry(window, textvariable=state.TAMAÑO_var)
    ui.tamaño_entry.configure(font=('Arial', 13))
    ui.tamaño_entry.grid(row=5, column=3)
    ui.producto_entry.bind(
            '<<ComboboxSelected>>',
            lambda event: on_product_selection(state, ui, data.stock, event))

    ui.cantidad_label = tk.Label(window, text="Cantidad")
    ui.cantidad_label.grid(row=6, column=3)
    ui.cantidad_entry = tk.Entry(window)
    ui.cantidad_entry.configure(font=('Arial', 13))
    ui.cantidad_entry.grid(row=7, column=3)
    ui.cantidad_entry.bind(
            '<Return>',
            lambda event: agregar_producto(ui, state, event))

    ui.precio_label = tk.Label(window, text="Precio por unidad")
    ui.precio_label.grid(row=4, column=4)
    ui.precio_entry = tk.Entry(window, textvariable=state.PRECIOB_var)
    ui.precio_entry.configure(font=('Arial', 13))
    ui.precio_entry.grid(row=5, column=4)

    ui.checkbox = tk.Checkbutton(
            window,
            text='Publico',
            variable=state.precio_bonificado_var,
            command=lambda: on_checkbox_change(state))
    ui.checkbox.grid(row=5, column=5)

    ui.checkboxiva = tk.Checkbutton(
            window,
            text='IVA',
            variable=state.precio_iva_var,
            command=lambda: on_checkbox_change(state))
    ui.checkboxiva.grid(row=6, column=5)

    ui.acreedor_deudor_label = tk.Label(window, text="Saldo anterior")
    ui.acreedor_deudor_label.grid(row=9, column=4)
    ui.acreedor_deudor_entry = tk.Entry(
            window,
            textvariable=state.acreedor_deudor_var)
    ui.acreedor_deudor_entry.configure(font=('Arial', 13))
    state.acreedor_deudor_var.trace(
            "w",
            lambda name, index, mode,
            sv=state.acreedor_deudor_var: logic.calcular_total(ui, state))
    ui.acreedor_deudor_entry.grid(row=10, column=4)

    ui.efectivo_label = tk.Label(window, text="Efectivo")
    ui.efectivo_label.grid(row=9, column=2)
    ui.efectivo_entry = tk.Entry(window, textvariable=state.efectivo_var)
    ui.efectivo_entry.configure(font=('Arial', 13))
    state.efectivo_var.trace(
            "w",
            lambda name, index, mode,
            sv=state.efectivo_var: logic.calcular_total(ui, state))
    ui.efectivo_entry.grid(row=10, column=2)

    ui.cheque_label = tk.Label(window, text="Cheque")
    ui.cheque_label.grid(row=9, column=1)
    ui.cheque_entry = tk.Entry(window, textvariable=state.cheque_var)
    ui.cheque_entry.configure(font=('Arial', 13))
    state.cheque_var.trace(
            "w",
            lambda name, index, mode,
            sv=state.cheque_var: logic.calcular_total(ui, state))
    ui.cheque_entry.grid(row=10, column=1)
    ui.cliente_entry.bind(
            '<<ComboboxSelected>>',
            lambda event: on_client_selection(ui, state, data, event))

    ui.agregar_button = tk.Button(
            window,
            text="Agregar",
            command=lambda: agregar_producto(ui, state))
    ui.agregar_button.grid(row=10, column=3)

    ui.style = ttk.Style()
    ui.style.configure("mystyle.Treeview", font=('Arial', 13))
    ui.style.configure("mystyle.Treeview.Heading", font=('Arial', 15, 'bold'))

    ui.factura_treeview = ttk.Treeview(
            window,
            columns=(
                'Fila',
                'Codigo',
                'Producto',
                'Tamaño',
                'Cantidad',
                'Precio',
                'Total'),
            show='headings',
            style="mystyle.Treeview")
    ui.factura_treeview.column('Codigo', width=150)
    ui.factura_treeview.column('Producto', width=500)
    ui.factura_treeview.column('Tamaño', width=100)
    ui.factura_treeview.column('Cantidad', width=150)
    ui.factura_treeview.column('Precio', width=150)
    ui.factura_treeview.column('Total', width=150)
    ui.factura_treeview.column('Fila', width=40)
    ui.factura_treeview.heading('Fila', text='Fila')
    ui.factura_treeview.heading('Codigo', text='Codigo')
    ui.factura_treeview.heading('Producto', text='Producto')
    ui.factura_treeview.heading('Tamaño', text='Tamaño')
    ui.factura_treeview.heading('Cantidad', text='Cantidad')
    ui.factura_treeview.heading('Precio', text='Precio')
    ui.factura_treeview.heading('Total', text='Total')
    ui.factura_treeview.grid(row=11, column=0, columnspan=6)
    ui.scrollbar = ttk.Scrollbar(
            window,
            orient="vertical",
            command=ui.factura_treeview.yview)
    ui.scrollbar.grid(row=11, column=7, sticky="ns")
    ui.factura_treeview.configure(yscrollcommand=ui.scrollbar.set)
    ui.factura_treeview.bind(
            '<Delete>',
            lambda event: borrar_fila(ui, state, event))

    ui.factura_treeview.grid(row=11, column=0, columnspan=6, sticky="nsew")
    ui.scrollbar.grid(row=11, column=7, sticky="ns")

    window.grid_rowconfigure(11, weight=1)
    window.grid_columnconfigure(3, weight=1)
    ui.factura_treeview.bind(
            '<Double-Button-1>',
            lambda event: editar_fila(window, ui, state, event))

    ui.dolares_entry = tk.Entry(window, textvariable=state.dolar_pag)
    ui.dolares_entry.configure(font=('Arial', 13))
    state.dolar_pag.trace(
            "w",
            lambda name, index, mode, sv=state.dolar_pag: logic.calcular_total(
                ui,
                state))
    ui.dolares_entry.grid(row=13, column=1)

    ui.total_label = tk.Label(window, text="Subtotal: 0")
    ui.total_label.configure(font=('Arial', 15))
    ui.total_label.grid(row=12, column=3)

    ui.totalisimo_label = tk.Label(window, text="Total: 0")
    ui.totalisimo_label.configure(font=('Arial', 15))
    ui.totalisimo_label.grid(row=12, column=4)

    ui.saldo_final_label = tk.Label(window, text="Saldo final: 0")
    ui.saldo_final_label.configure(font=('Arial', 15))
    ui.saldo_final_label.grid(row=12, column=5)

    ui.button_buscar = tk.Button(
            window,
            text="En dolares",
            command=lambda: web.buscar_valor(ui, state))
    ui.button_buscar.grid(row=13, column=2)

    ui.print_button = tk.Button(
            window,
            text="Imprimir boleta",
            command=lambda: print_invoice(ui, state, data))
    ui.print_button.grid(row=13, column=5)

    ui.open_button = tk.Button(
            window,
            text="Ver PDF",
            command=lambda: open_invoice(ui, state, data))
    ui.open_button.grid(row=13, column=4)

    return window
