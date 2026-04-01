from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Headers para que los bancos nos vean como un usuario real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- 1. BANCO NACIÓN (Scraping de HTML) ---
        try:
            res_bna = requests.get("https://www.bna.com.ar/Personas", headers=headers, timeout=10)
            if res_bna.status_code == 200:
                soup = BeautifulSoup(res_bna.text, 'html.parser')
                # Buscamos la tabla que tiene la clase 'cotizacion'
                tabla = soup.find('table', {'class': 'cotizacion'})
                if not tabla:
                    # Intento alternativo si cambiaron la clase
                    tabla = soup.find('table', {'class': 'table'})
                
                if tabla:
                    for fila in tabla.find_all('tr'):
                        tds = fila.find_all('td')
                        if tds and "Dolar U.S.A" in tds[0].text:
                            # Limpieza: "$ 1.355,00" -> 1355.0
                            compra = float(tds[1].text.strip().replace('.', '').replace(',', '.'))
                            venta = float(tds[2].text.strip().replace('.', '').replace(',', '.'))
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

        # --- 2. BANCO BBVA (Acceso a API interna) ---
        try:
            # Esta es la URL que alimenta el visor del BBVA
            url_api_bbva = "https://www.bbva.com.ar/api/comunes/v1/cotizaciones"
            headers_bbva = headers.copy()
            headers_bbva['Referer'] = 'https://www.bbva.com.ar/'
            
            res_bbva = requests.get(url_api_bbva, headers=headers_bbva, timeout=10)
            if res_bbva.status_code == 200:
                data = res_bbva.json()
                for item in data.get('cotizaciones', []):
                    # Buscamos el objeto "Dólar"
                    if "Dólar" in item.get('descripcion', ''):
                        resultados.append({
                            "banco": "BBVA",
                            "compra": float(item['compra']),
                            "venta": float(item['venta']),
                            "color": "#004481",
                            "updated": ahora
                        })
                        break
        except Exception as e:
            print(f"Error BBVA: {e}")

        # ENVÍO DE RESPUESTA
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # CORS para que tu HTML lo lea
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
