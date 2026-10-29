import ui
import data as db


def main():
    data = db.init_tables()

    window = ui.init(data)

    window.mainloop()


main()
