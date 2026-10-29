import config
import math
import ui


def public_price(price):
    return float(math.ceil((float(price) * config.recargo) /
                           config.redondeo) * config.redondeo)


def add_IVA(price):
    return (float(price*config.redondeo) * config.IVA)/config.redondeo


def decide_price(price, is_retail, has_IVA):
    if is_retail == 1 and has_IVA == 0:
        result = public_price(price)
    elif has_IVA == 1 and is_retail == 0:
        result = add_IVA(price)
    elif has_IVA == 1 and is_retail == 1:
        result = add_IVA(public_price(price))
    else:
        result = price
    return result


def calcular_total(ui_elements, state):
    total = 0.0
    totalisimo = 0.0
    pagoe = 0.0
    pagoch = 0.0
    saldo = state.acreedor_deudor_var.get()
    saldo = '0' if saldo == '' else saldo
    saldot = 0.0
    pagod = 0.0
    dolprom = 0.0
    total = ui.sum_column_from_ui_table(ui_elements, 6)
    totalisimo = round(float(total) - float(saldo), 2)
    dolprom = state.dolar_var.get()
    pagod = state.dolar_pag.get()
    pagod = '0' if pagod == '' else pagod
    pagodars = float(dolprom) * float(pagod)
    pagoe = state.efectivo_var.get()
    pagoch = state.cheque_var.get()
    pagoe = '0' if pagoe == '' else pagoe
    pagoch = '0' if pagoch == '' else pagoch
    pagodars = '0' if pagodars == '' else pagodars
    pagot = float(pagoe) + float(pagoch) + float(pagodars)
    saldot = round(-float(totalisimo) + float(pagot), 2)
    totales = [total, totalisimo, saldot]
    ui.update_bill_sum(ui_elements, totales)
    return totalisimo
