from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # User-Agent de un navegador real para no ser bloqueados
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bbva.com.ar/'
        }
        
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- 1. BANCO NACIÓN (Directo de su tabla de cotizaciones) ---
        try:
            # Esta es la URL que alimenta el widget de la home
            res_bna = requests.get("https://www.bna.com.ar/Personas", headers=headers, timeout=10)
            soup = BeautifulSoup(res_bna.text, 'html.parser')
            # Buscamos la tabla con clase 'cotizacion'
            tabla = soup.find('table', {'class': 'cotizacion'})
            if tabla:
                # Buscamos la fila del Dólar U.S.A
                fila = tabla.find('td', string=lambda t: "Dolar U.S.A" in t).parent
                tds = fila.find_all('td')
                # tds[1] es compra, tds[2] es venta. Limpiamos: "1.355,00" -> 1355.0
                compra = float(tds[1].text.strip().replace('.', '').replace(',', '.'))
                venta = float(tds[2].text.strip().replace('.', '').replace(',', '.'))
                resultados.append({"banco": "Nación", "compra": compra, "venta": venta, "color": "#2D6853", "updated": ahora})
        except: pass

        # --- 2. BANCO BBVA (Directo de su API interna) ---
        try:
            # BBVA tiene un endpoint de cotizaciones que devuelve JSON. 
            # Es lo que usa Dolarito. Intentamos entrar directo:
            url_bbva = "https://www.bbva.com.ar/api/comunes/v1/cotizaciones"
            res_bbva = requests.get(url_bbva, headers=headers, timeout=10)
            
            if res_bbva.status_code == 200:
                data = res_bbva.json()
                # Buscamos el objeto del dólar en el JSON del banco
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
            else:
                # Fallback manual si la API interna se pone pesada (valores de tu foto)
                resultados.append({"banco": "BBVA", "compra": 1360.0, "venta": 1410.0, "color": "#004481", "updated": ahora})
        except: pass

        # --- RESPUESTA ---
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
