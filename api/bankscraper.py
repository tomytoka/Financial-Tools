from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- BANCO NACIÓN (REAL SCRAPING) ---
        try:
            # Entramos a la web de cotizaciones del BNA
            res = requests.get("https://www.bna.com.ar/Cotizador/MonedasHistorico", headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Buscamos la fila que dice "Dolar U.S.A"
            fila_dolar = soup.find('td', string="Dolar U.S.A").parent
            celdas = fila_dolar.find_all('td')
            
            # celdas[1] es Compra, celdas[2] es Venta
            compra_bna = float(celdas[1].text.replace(',', '.'))
            venta_bna = float(celdas[2].text.replace(',', '.'))
            
            resultados.append({
                "banco": "Nación", 
                "compra": compra_bna, 
                "venta": venta_bna, 
                "color": "#2D6853", 
                "updated": ahora
            })
        except Exception as e:
            print(f"Error BNA: {e}")

        # --- BANCO BBVA (REAL SCRAPING) ---
        try:
            res = requests.get("https://www.bbva.com.ar/personas/productos/inversiones/cotizacion-moneda-extranjera.html", headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # El BBVA suele usar clases de CSS para los precios. 
            # IMPORTANTE: Estos nombres de clase (.cuadro-cotizacion, etc) cambian seguido.
            # Aquí buscamos el texto que contiene el signo $
            precios = soup.find_all(string=lambda t: "$" in t)
            # Limpiamos el texto para quedarnos solo con el número
            compra_bbva = float(precios[0].replace('$', '').replace('.', '').replace(',', '.'))
            venta_bbva = float(precios[1].replace('$', '').replace('.', '').replace(',', '.'))

            resultados.append({
                "banco": "BBVA", 
                "compra": compra_bbva, 
                "venta": venta_bbva, 
                "color": "#004481", 
                "updated": ahora
            })
        except:
            pass

        # Respuesta final
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
