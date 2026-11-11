import ui
import data as db


def main():

    fields = {}
    fields['numero'] = 'NUMERO'
    fields['razon'] = 'RAZON'
    fields['ncuit'] = 'NCUIT'
    fields['deudor'] = 'DEUDOR'
    fields['acreedor'] = 'ACREEDOR'

    data = db.init_tables('CLIPRO.DBF', fields)

    window = ui.init(data)

    window.mainloop()


main()
