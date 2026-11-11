import requests
from bs4 import BeautifulSoup
import logic
import ui


def buscar_valor(ui_context, state):
    """Busca los valores de compra y venta del dólar blue."""
    # url = "https://dolarhoy.com/cotizaciondolarblue"
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

            # compra = float(compra.replace('$', '').replace(',', '.'))
            # venta = float(venta.replace('$', '').replace(',', '.'))

            spanish_price = str.maketrans({'$': None, '.': None, ',': '.'})

            compra = float(compra.translate(spanish_price))
            venta = float(venta.translate(spanish_price))

            promedio = (compra + venta) / 2

            state.dolar_var.set(promedio)

            saldot = logic.calcular_total(ui_context, state) / promedio
            ui.show_message(
                    "Resultado",
                    f"Compra: {compra}\nVenta:" +
                    f" {venta}\nPromedio: {promedio}\n" +
                    f"\n A pagar: {saldot}")
        else:
            ui.show_message(
                    "Resultado", "No se pudieron obtener los" +
                    " valores de compra y venta.")

    except requests.exceptions.RequestException as e:
        ui.show_message("Error", f"Error al acceder a la URL: {e}")
    except ValueError as e:
        ui.show_message("Error", f"Error al convertir valores a números: {e}")
    except Exception as e:
        ui.show_message("Error", f"Error inesperado: {e}")
