from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Headers para "camuflar" el robot como un humano
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept-Language': 'es-AR,es;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- 1. BANCO NACIÓN (FUNCIONA) ---
        try:
            res = requests.get("https://www.bna.com.ar/Personas", headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Buscamos la tabla con clase 'cotizacion'
            tabla = soup.find('table', {'class': 'cotizacion'})
            if tabla:
                for fila in tabla.find_all('tr'):
                    tds = fila.find_all('td')
                    if tds and "Dolar U.S.A" in tds[0].text:
                        c = float(tds[1].text.strip().replace('.', '').replace(',', '.'))
                        v = float(tds[2].text.strip().replace('.', '').replace(',', '.'))
                        resultados.append({"banco": "Nación", "compra": c, "venta": v, "color": "#2D6853", "updated": ahora})
                        break
        except: pass

        # --- 2. BANCO PROVINCIA (NUEVO - SUELE FUNCIONAR) ---
        try:
            # El BAPRO tiene una página muy simple de cotizaciones
            res_p = requests.get("https://www.bancoprovincia.com.ar/Principal/Dolar", headers=headers, timeout=10)
            soup_p = BeautifulSoup(res_p.text, 'html.parser')
            # Buscamos los valores en los inputs o textos de la página
            # Nota: Esta es una simplificación, el BAPRO a veces usa una tabla simple
            tds = soup_p.find_all('td')
            if tds:
                # El BAPRO suele tener Compra en el primer TD y Venta en el segundo
                c = float(tds[0].text.replace('$','').strip().replace(',','.'))
                v = float(tds[1].text.replace('$','').strip().replace(',','.'))
                resultados.append({"banco": "Provincia", "compra": c, "venta": v, "color": "#129e46", "updated": ahora})
        except: pass

        # --- 3. BANCO BBVA (EXPERIMENTAL) ---
        try:
            # Intentamos entrar a su API pública de nuevo con headers más agresivos
            url_bbva = "https://www.bbva.com.ar/api/comunes/v1/cotizaciones"
            res_b = requests.get(url_bbva, headers=headers, timeout=10)
            if res_b.status_code == 200:
                data = res_b.json()
                for item in data.get('cotizaciones', []):
                    if "Dólar" in item.get('descripcion', ''):
                        resultados.append({
                            "banco": "BBVA", 
                            "compra": float(item['compra']), 
                            "venta": float(item['venta']), 
                            "color": "#004481", 
                            "updated": ahora
                        })
                        break
        except: pass

        # RESPUESTA
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
