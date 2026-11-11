import os
import shutil
from dbfread import DBF
import dbf
from dataclasses import dataclass
import ui


@dataclass
class tables:
    stock: list
    clipro: list
    fields: dict


def init_tables(cli_pro, fields):
    files = {
            'stock': 'STOCK1.DBF',
            'clipro': cli_pro}

    data = {}

    current_dir = os.path.dirname(os.path.realpath(__file__))

    for atrr, filename in files.items():
        original_path = os.path.join(current_dir, filename)
        temp_path = os.path.join(current_dir, f'temp_{filename}')

        # Abrir y leer la copia temporal dentro de un bloque 'with'
        with DBF(original_path, encoding='cp850', load=True) as database:
            data[atrr] = database.records

        # Ahora que el objeto DBF está cerrado, se puede copiar el archivo
        shutil.copyfile(original_path, temp_path)

    data['fields'] = fields

    return tables(**data)  # Should look up the meaning of **data in python


def actualizar_stock(data, ui_context):
    print("Ejecutando actualizar_stock")
    stock_updates = {}
    for row in ui.get_prod_entries_indexes(ui_context):
        values = ui.get_prod_entries_row(ui_context, row)  # expects a tuple
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
