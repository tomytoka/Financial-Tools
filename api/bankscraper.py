from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # User-Agent para que el banco no piense que somos un ataque
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- SCRAPING REAL BANCO NACIÓN ---
        try:
            # Usamos la URL que me pasaste
            url_bna = "https://www.bna.com.ar/Personas"
            res = requests.get(url_bna, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            # Buscamos la tabla que está en el visor de la foto
            # El BNA usa una clase 'table cotizacion' para ese widget
            tabla = soup.find('table', {'class': 'table cotizacion'})
            
            if tabla:
                # Buscamos la fila que dice "Dolar U.S.A"
                for fila in tabla.find_all('tr'):
                    columnas = fila.find_all('td')
                    if len(columnas) > 0 and "Dolar U.S.A" in columnas[0].text:
                        # Limpieza de datos: BNA usa ',' para decimales y '.' para miles
                        # Ejemplo: "1.355,00" -> "1355.00"
                        compra_raw = columnas[1].text.strip().replace('.', '').replace(',', '.')
                        venta_raw = columnas[2].text.strip().replace('.', '').replace(',', '.')
                        
                        resultados.append({
                            "banco": "Nación",
                            "compra": float(compra_raw),
                            "venta": float(venta_raw),
                            "color": "#2D6853",
                            "updated": ahora
                        })
                        break
        except Exception as e:
            print(f"Error scraping BNA: {e}")

        # --- LOS OTROS BANCOS (BBVA, ICBC, ETC) ---
        # Como te conté, estos bancos usan JavaScript (React/Angular) 
        # y Python 'requests' no puede ver los precios porque no ejecuta JS.
        # Para que tu dashboard no esté vacío, acá te sugiero scrapear 
        # una fuente que SÍ sea estática y tenga a todos los bancos, como 'Ámbito'.
        
        try:
            # Ejemplo de scraping de una fuente secundaria más estable
            res_amb = requests.get("https://www.ambito.com/contenidos/dolar-bancos.html", headers=headers, timeout=10)
            # Aquí iría la lógica para sacar BBVA, Galicia, etc. de Ámbito.
            # Por ahora, te dejo el BNA que es el que ya logramos 'domar'.
        except:
            pass

        # RESPUESTA JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
