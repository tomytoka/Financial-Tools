from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Headers que imitan a un navegador real (Crucial para no ser bloqueado)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- 1. BANCO NACIÓN (Desde /Personas) ---
        try:
            res_bna = requests.get("https://www.bna.com.ar/Personas", headers=headers, timeout=15)
            if res_bna.status_code == 200:
                soup = BeautifulSoup(res_bna.text, 'html.parser')
                # Buscamos la tabla con clase 'cotizacion' que es la del visor
                tabla = soup.find('table', {'class': 'table cotizacion'})
                if tabla:
                    # Buscamos la fila que contiene el texto del Dólar
                    for fila in tabla.find_all('tr'):
                        columnas = fila.find_all('td')
                        if columnas and "Dolar U.S.A" in columnas[0].text:
                            # Parseo real de los valores del HTML
                            compra = float(columnas[1].text.strip().replace('.', '').replace(',', '.'))
                            venta = float(columnas[2].text.strip().replace('.', '').replace(',', '.'))
                            resultados.append({
                                "banco": "Nación",
                                "compra": compra,
                                "venta": venta,
                                "color": "#2D6853",
                                "updated": ahora
                            })
                            break
        except Exception as e:
            print(f"Error BNA: {e}")

        # --- 2. BANCO BBVA (Intento de Scraping de Tabla) ---
        try:
            url_bbva = "https://www.bbva.com.ar/personas/productos/inversiones/cotizacion-moneda-extranjera.html"
            res_bbva = requests.get(url_bbva, headers=headers, timeout=15)
            if res_bbva.status_code == 200:
                soup = BeautifulSoup(res_bbva.text, 'html.parser')
                # Buscamos todas las tablas y filtramos por la que tiene los precios
                tablas = soup.find_all('table')
                for t in tablas:
                    for fila in t.find_all('tr'):
                        tds = fila.find_all('td')
                        if tds and ("Dólar" in tds[0].text or "U$S" in tds[0].text):
                            # Si encuentra la fila, extrae los valores
                            c_text = tds[1].text.replace('$','').strip().replace('.','').replace(',','.')
                            v_text = tds[2].text.replace('$','').strip().replace('.','').replace(',','.')
                            resultados.append({
                                "banco": "BBVA",
                                "compra": float(c_text),
                                "venta": float(v_text),
                                "color": "#004481",
                                "updated": ahora
                            })
                            break
        except Exception as e:
            print(f"Error BBVA: {e}")

        # ENVÍO DE RESPUESTA (Solo los que se pudieron scrapear de verdad)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
