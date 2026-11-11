import ui
import data as db


def main():

    fields = {}
    fields['numero'] = 'NUMERO'
    fields['razon'] = 'RAZON'
    fields['ncuit'] = 'NCUIT'
    fields['deudor'] = 'SGDEUD'
    fields['acreedor'] = 'SGACRE'

    data = db.init_tables('PROVE.DBF', fields)

    window = ui.init(data)

    window.mainloop()


main()
