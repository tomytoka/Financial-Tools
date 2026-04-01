from http.server import BaseHTTPRequestHandler
import requests
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Headers de "Navegador Real" - Indispensables para que el banco no nos rechace
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'application/json', # Le decimos que queremos el dato puro
            'Referer': 'https://www.bbva.com.ar/personas/productos/inversiones/cotizacion-moneda-extranjera.html'
        }
        
        resultados = []
        ahora = datetime.now().strftime("%H:%M")

        # --- 1. BANCO NACIÓN (Sigue igual porque funciona) ---
        try:
            # (Acá mantené tu código del Nación que ya te funciona)
            # Solo asegúrate de que use 'requests' para sacar el dato real.
            pass 
        except: pass

        # --- 2. BANCO BBVA (Acceso Directo a los Datos) ---
        try:
            # Esta es la URL "secreta" que usa el BBVA para llenar su tablita
            # Es lo que descubrís haciendo F12 > Network en el navegador
            url_api_bbva = "https://www.bbva.com.ar/api/comunes/v1/cotizaciones"
            res_bbva = requests.get(url_api_bbva, headers=headers, timeout=15)
            
            if res_bbva.status_code == 200:
                data = res_bbva.json()
                # El banco devuelve una lista de cotizaciones. Buscamos el Dólar.
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
        except Exception as e:
            # Si falla, no ponemos nada. El dashboard simplemente no mostrará el BBVA.
            print(f"Error técnico BBVA: {e}")

        # ENVÍO DE RESPUESTA
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultados).encode())
